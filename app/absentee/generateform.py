import io
from typing import Any, Dict, Optional

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.files import File
from django.template.defaultfilters import slugify

from common import enums
from common.analytics import statsd
from common.pdf import PDFTemplate
from election.models import StateInformation
from multi_tenant.models import Client
from official.models import Address
from storage.models import StorageItem


class NoAbsenteeRequestMailingAddress(Exception):
    pass


COVER_SHEET_PATH = "absentee/templates/pdf/cover.pdf"


def generate_name(state_code: str, last_name: str):
    filename = slugify(f"{state_code} {last_name} ballotrequest").lower()
    return f"{filename}.pdf"


@statsd.timed("turnout.absentee.absentee_application_pdfgeneration")
def generate_pdf(form_data: Dict[str, Any], state_code: str) -> io.BytesIO:
    return PDFTemplate(
        [COVER_SHEET_PATH, f"absentee/templates/pdf/states/{state_code}.pdf"]
    ).fill(form_data)


def prepare_formdata(region_external_id: str, state_code: str) -> Dict[str, Any]:
    form_data: Dict[str, Any] = {}

    # find the mailing address

    mailing_addresses = Address.objects.filter(
        office__region__external_id=region_external_id, process_absentee_requests=True
    )
    if len(mailing_addresses) == 0:
        raise NoAbsenteeRequestMailingAddress(
            f"No absentee request mailing address for region {region_external_id}"
        )

    mailing_address = mailing_addresses[0]

    mailto_lines = [
        line
        for line in [
            mailing_address.address,
            mailing_address.address2,
            mailing_address.address3,
            f"{mailing_address.city.title()}, {mailing_address.state.code} {mailing_address.zipcode}",
        ]
        if line is not None and len(line) > 0
    ]

    for num, line in enumerate(mailto_lines):
        form_data[f"mailto_line_{num+1}"] = line

    # Find the application deadline

    try:
        state_mail_deadline = (
            StateInformation.objects.only("field_type", "text")
            .get(state=state_code, field_type__slug="vbm_deadline_mail")
            .text.lower()
        )

        # TODO: are the deadlines mail-by or arrive-by? Putting arrive-by here
        # becuase that's more conservative
        state_deadline = f"Your form must arrive by {state_mail_deadline}."
    except StateInformation.DoesNotExist:
        state_deadline = "Mail your form as soon as possible."

    form_data["state_deadlines"] = state_deadline

    return form_data


# TODO: this should take the absentee request model object instead of a ton
# of arguments
def prepare_absentee_request_form(
    region_external_id: str,
    state_code: str,
    last_name: str,
    email: str,
    partner: Optional[Client] = None,
) -> StorageItem:
    form_data = prepare_formdata(region_external_id, state_code)

    filled_pdf = generate_pdf(form_data, state_code)
    item = StorageItem(
        app=enums.FileType.ABSENTEE_REQUEST_FORM, email=email, partner=partner,
    )
    item.file.save(generate_name(state_code, last_name), File(filled_pdf), True)

    return item
