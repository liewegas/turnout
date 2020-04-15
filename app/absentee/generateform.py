import logging
from typing import IO, TYPE_CHECKING, Any, Dict, Optional

from django.core.files import File
from django.template.defaultfilters import slugify

from common import enums
from common.analytics import statsd
from common.pdf import PDFTemplate, PDFTemplateSection
from election.models import StateInformation
from official.models import Address
from storage.models import StorageItem

from .models import BallotRequest

logger = logging.getLogger("absentee")


class NoAbsenteeRequestMailingAddress(Exception):
    pass


COVER_SHEET_PATH = "absentee/templates/pdf/cover.pdf"


def generate_name(state_code: str, last_name: str):
    """
    Generates a name for the PDF
    """
    filename = slugify(f"{state_code} {last_name} ballotrequest").lower()
    return f"{filename}.pdf"


def state_text_property(state_code: str, slug: str, lower=False) -> Optional[str]:
    """
    Helper to read a sigle StateInformation field
    """
    try:
        text = (
            StateInformation.objects.only("field_type", "text")
            .get(state=state_code, field_type__slug=slug)
            .text
        )

        if lower:
            text = text.lower()

        return text
    except StateInformation.DoesNotExist:
        return "As soon as possible."


def absentee_address_score(addr: Address) -> int:
    """
    Returns a "score" for how appropriate it is to talk to this Address about
    absentee ballots.

    1: This is an office that accept absentee ballot forms by mail
    2: This is an office that processes absentee ballot forms
    3: All other offices

    We will only tell users to mail to offices with a score of 1, but we may
    give them contact info for 2's and 3's if there are no 1's with contact
    info.
    """
    if addr.process_absentee_requests and addr.is_regular_mail:
        return 1
    elif addr.process_absentee_requests:
        return 2
    else:
        return 3


def prepare_formdata(region_external_id: str, state_code: str) -> Dict[str, Any]:
    """
    Assembles all the form data we need to fill out an absentee ballot request
    form.
    """
    form_data: Dict[str, Any] = {}

    # find the mailing address
    office_addresses = Address.objects.filter(
        office__region__external_id=region_external_id
    )

    absentee_mailing_addresses = [
        addr for addr in office_addresses if absentee_address_score(addr) == 1
    ]

    if len(absentee_mailing_addresses) == 0:
        raise NoAbsenteeRequestMailingAddress(
            f"No absentee request mailing address for region {region_external_id}"
        )

    absentee_mailing_address = absentee_mailing_addresses[0]
    form_data["vbm_submission_address"] = "\n".join(
        [
            line
            for line in [
                absentee_mailing_address.address,
                absentee_mailing_address.address2,
                absentee_mailing_address.address3,
                f"{absentee_mailing_address.city.title()}, {absentee_mailing_address.state.code} {absentee_mailing_address.zipcode}",
            ]
            if line is not None and len(line) > 0
        ]
    )

    # Find contact info
    email = next((addr.email for addr in office_addresses if addr.email), None)
    phone = next((addr.phone for addr in office_addresses if addr.phone), None)

    if email or phone:
        contact_info_lines = []
        if email:
            contact_info_lines.append(f"Email: {email}")
        if phone:
            contact_info_lines.append(f"Phone: {phone}")

        form_data["vbm_contact_info"] = "\n".join(contact_info_lines)
    else:
        form_data[
            "vbm_contact_info"
        ] = "https://www.usvotefoundation.org/vote/eoddomestic.htm"

    # Find state-specific info
    form_data["vbm_deadline"] = (
        state_text_property(state_code, "vbm_deadline_mail", lower=True)
        or "As soon as possible."
    )

    # If we don't have data, make the most conservative assumption: 55 days before the election
    form_data["vbm_first_day_to_apply"] = (
        state_text_property(state_code, "vbm_first_day_to_apply", lower=True)
        or "At least 55 days before the election."
    )

    return form_data


@statsd.timed("turnout.absentee.absentee_application_pdfgeneration")
def generate_pdf(form_data: Dict[str, Any], state_code: str) -> IO:
    return PDFTemplate(
        [
            PDFTemplateSection(path=COVER_SHEET_PATH, is_form=True),
            PDFTemplateSection(path=f"absentee/templates/pdf/states/{state_code}.pdf"),
        ]
    ).fill(form_data)


def process_ballot_request(ballot_request: BallotRequest,):
    form_data = prepare_formdata(
        ballot_request.region.external_id, ballot_request.state.code
    )

    with generate_pdf(form_data, ballot_request.state.code) as filled_pdf:
        item = StorageItem(
            app=enums.FileType.ABSENTEE_REQUEST_FORM,
            email=ballot_request.email,
            partner=ballot_request.partner,
        )
        item.file.save(
            generate_name(ballot_request.state.code, ballot_request.last_name),
            File(filled_pdf),
            True,
        )

    ballot_request.result_item = item
    ballot_request.save(update_fields=["result_item"])

    # send_registration_notification.delay(ballot_request.pk)

    logger.info(f"New PDF Created: Ballot Request {item.pk} ({item.download_url})")
