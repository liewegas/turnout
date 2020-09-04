from celery import shared_task

from absentee.models import BallotRequest
from action.models import Action
from register.models import Registration
from reminder.models import ReminderRequest
from verifier.models import Lookup

from .actionnetwork import sync, sync_all_items, sync_item


@shared_task
def sync_lookup_to_actionnetwork(pk: str) -> None:
    sync_item(Lookup.objects.get(uuid=pk))


@shared_task
def sync_ballotrequest_to_actionnetwork(pk: str) -> None:
    sync_item(BallotRequest.objects.get(uuid=pk))


@shared_task
def sync_registration_to_actionnetwork(pk: str) -> None:
    sync_item(Registration.objects.get(uuid=pk))


@shared_task
def sync_reminderrequest_to_actionnetwork(pk: str) -> None:
    sync_item(ReminderRequest.objects.get(uuid=pk))


@shared_task
def sync_action_to_actionnetwork(pk: str) -> None:
    action = Action.objects.get(pk=pk)
    sync_item(action.get_source_item())


@shared_task
def sync_actionnetwork():
    sync()


@shared_task
def sync_actionnetwork_registrations():
    sync_all_items(Registration)


@shared_task
def sync_actionnetwork_lookups():
    sync_all_items(Lookup)


@shared_task
def sync_actionnetwork_ballotrequests():
    sync_all_items(BallotRequest)


@shared_task
def sync_actionnetwork_reminderrequests():
    sync_all_items(ReminderRequest)
