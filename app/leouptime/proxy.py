import datetime
import logging
import random
import tempfile
import time
import uuid

import paramiko
import requests
from django.conf import settings

from common import enums

from .models import Proxy

PROXY_PORT = 4455
CREATE_TEMPLATE = {
    "size": "s-1vcpu-1gb",
    "image": "ubuntu-18-04-x64",
    "ssh_keys": [settings.PROXY_SSH_KEY_ID],
    "backups": False,
    "ipv6": False,
}
PROXY_PREFIX = "proxy-"

DROPLET_ENDPOINT = "https://api.digitalocean.com/v2/droplets"

UNITFILE = f"""
[Unit]
Description=microsocks
After=network.target
[Service]
ExecStart=/root/microsocks/microsocks -p {PROXY_PORT}
[Install]
WantedBy=multi-user.target
"""

SETUP = [
    "apt update",
    "apt install -y gcc make",
    "git clone https://github.com/rofl0r/microsocks",
    "cd microsocks && make",
    "systemctl enable microsocks.service",
    "systemctl start microsocks.service",
]

logger = logging.getLogger("leouptime")


REGIONS = [
    "nyc1",
    "nyc3",
    "sfo2",
    "sfo3",
]


def get_proxies_by_name():
    response = requests.get(
        DROPLET_ENDPOINT,
        headers={
            "Authorization": f"Bearer {settings.DIGITALOCEAN_KEY}",
            "Content-Type": "application/json",
        },
    )
    r = {}
    for droplet in response.json()["droplets"]:
        r[droplet["name"]] = droplet
    return r


def create_proxy(region):
    name = f"{PROXY_PREFIX}{region}-{str(uuid.uuid4())}"

    logger.info(f"Creating {name}...")
    req = CREATE_TEMPLATE.copy()
    req["name"] = name
    req["region"] = region
    response = requests.post(
        DROPLET_ENDPOINT,
        headers={
            "Authorization": f"Bearer {settings.DIGITALOCEAN_KEY}",
            "Content-Type": "application/json",
        },
        json=req,
    )
    logger.info(response.json())
    droplet_id = response.json()["droplet"]["id"]

    # wait for IP address
    logger.info(f"Created {name} droplet_id {droplet_id}, waiting for IP...")
    ip = None
    while True:
        response = requests.get(
            f"{DROPLET_ENDPOINT}/{droplet_id}",
            headers={
                "Authorization": f"Bearer {settings.DIGITALOCEAN_KEY}",
                "Content-Type": "application/json",
            },
        )
        for v4 in response.json()["droplet"]["networks"].get("v4", []):
            ip = v4["ip_address"]
            break
        if ip:
            break
        logger.info("waiting for IP")
        time.sleep(1)

    proxy = Proxy.objects.create(
        proxy=f"{ip}:{PROXY_PORT}",
        description=name,
        state=enums.ProxyStatus.CREATING,
        failure_count=0,
    )

    with tempfile.NamedTemporaryFile() as tmp_key:
        tmp_key.write(settings.PROXY_SSH_KEY.replace("\\n", "\n").encode("utf-8"))
        tmp_key.flush()

        # logger.info(f"IP is {ip}, waiting for machine to come up...")
        # time.sleep(60)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        while True:
            try:
                logger.info(f"Connecting to {ip} via SSH...")
                ssh.connect(ip, username="root", key_filename=tmp_key.name, timeout=10)
                break
            except:
                logger.info("Waiting a bit...")
                time.sleep(5)

        logger.info("Writing systemd unit...")
        stdin_, stdout_, stderr_ = ssh.exec_command(
            "cat >/etc/systemd/system/microsocks.service"
        )
        stdin_.write(UNITFILE)
        stdin_.close()
        stdout_.channel.recv_exit_status()

        for cmd in SETUP:
            stdin_, stdout_, stderr_ = ssh.exec_command(cmd)
            stdout_.channel.recv_exit_status()
            lines = stdout_.readlines()
            logger.info(f"{cmd}: {lines}")

    proxy.state = enums.ProxyStatus.UP
    proxy.save()
    logger.info(f"Created proxy {proxy.proxy} ({proxy.description})")
    return proxy


def remove_proxy(droplet_id):
    response = requests.delete(
        f"{DROPLET_ENDPOINT}/{droplet_id}/destroy_with_associated_resources/dangerous",
        headers={
            "Authorization": f"Bearer {settings.DIGITALOCEAN_KEY}",
            "Content-Type": "application/json",
            "X-Dangerous": "true",
        },
    )


def check_proxies():
    stray = get_proxies_by_name()
    up = 0
    creating_cutoff = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc
    ) - datetime.timedelta(minutes=10)
    for proxy in Proxy.objects.all():
        if proxy.description in stray:
            logger.info(f"Have proxy {proxy.proxy} {proxy.description} {proxy.state}")
            if proxy.state == enums.ProxyStatus.BURNED:
                # we should delete this
                proxy.state = enums.ProxyStatus.DOWN
                proxy.save()
            elif proxy.state == enums.ProxyStatus.DOWN:
                # we should delete this
                pass
            elif (
                proxy.state == enums.ProxyStatus.CREATING
                and proxy.modified_at < creating_cutoff
            ):
                # delete
                logger.info("Proxy {proxy.proxy} has been CREATING for too long")
                proxy.state = enums.ProxyStatus.DOWN
                proxy.save()
            else:
                # not stray
                if proxy.state == enums.ProxyStatus.UP:
                    up += 1
                del stray[proxy.description]
        else:
            if proxy.state != enums.ProxyStatus.DOWN:
                logger.info(f"No droplet for proxy {proxy.proxy} {proxy.description}")
                proxy.state = enums.ProxyStatus.DOWN
                proxy.save()
    while up < settings.PROXY_COUNT:
        create_proxy(random.choice(REGIONS))
        up += 1

    for name, info in stray.items():
        if not name.startswith(PROXY_PREFIX):
            continue
        logger.info(f"Removing stray droplet {info['id']}")
        remove_proxy(info["id"])
