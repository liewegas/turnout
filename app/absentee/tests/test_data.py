import datetime
import os
from typing import Any, Dict, List, Tuple

from model_bakery import baker

from absentee.models import BallotRequest
from election.choices import STATES
from election.models import State, StateInformation
from official.baker_recipes import (
    ABSENTEE_BALLOT_MAILING_ADDRESS,
    ABSENTEE_BALLOT_MAILING_CITY_STATE_ZIP,
)

from ..state_pdf_data import STATE_DATA

TEST_BALLOT_REQUEST_STATE_ID_NUMBER = "1234"
TEST_BALLOT_REQUEST_IS_18_OR_OVER = True

STATES_WITH_METADATA = (
    os.environ["ABSENTEE_TEST_ONLY"].split(",")
    if os.environ.get("ABSENTEE_TEST_ONLY")
    else STATE_DATA.keys()
)

ALL_STATES = (
    os.environ["ABSENTEE_TEST_ONLY"].split(",")
    if os.environ.get("ABSENTEE_TEST_ONLY")
    else [state_code for state_code, state_name in STATES]
)


def add_state_info(state: State, slug: str, value: str):
    ft = baker.make_recipe("election.markdown_field_type", slug=slug)

    info = StateInformation.objects.get(state=state.code, field_type=ft.uuid)
    info.text = value
    info.save()


def make_test_data(state=None) -> Tuple[BallotRequest, Dict[str, Any]]:
    addr = baker.make_recipe("official.absentee_ballot_address")

    if state is None:
        state = baker.make_recipe("election.state")

    add_state_info(state, "vbm_deadline_mail", "Some DEADLINE")
    add_state_info(state, "vbm_first_day_to_apply", "Some DATE")

    ballot_request = baker.make_recipe(
        "absentee.ballot_request",
        region=addr.office.region,
        first_name="some_first_name",
        middle_name="some_middle_name",
        last_name="some_last_name",
        suffix="III",
        date_of_birth=datetime.date(1992, 5, 10),
        email="foo@example.com",
        phone="(617) 555-1234",
        address1="some addr 1",
        address2="some addr 2",
        city="some city",
        state=state,
        zipcode="12345",
        mailing_address1="some mailing addr",
        mailing_address2="some mailing addr 2",
        mailing_city="some mailing city",
        mailing_state=state,
        mailing_zipcode="67890",
        us_citizen=True,
        sms_opt_in=True,
        submit_date=datetime.date(2020, 4, 15),
    )

    expected_data = {
        "first_name": "some_first_name",
        "middle_name": "some_middle_name",
        "last_name": "some_last_name",
        "suffix": "III",
        "date_of_birth": "05/10/1992",
        "email": "foo@example.com",
        "phone": "(617) 555-1234",
        "address1": "some addr 1",
        "address2": "some addr 2",
        "city": "some city",
        "state": state.code,
        "zipcode": "12345",
        "mailing_address1": "some mailing addr",
        "mailing_address2": "some mailing addr 2",
        "mailing_city": "some mailing city",
        "mailing_state": state.code,
        "mailing_zipcode": "67890",
        "us_citizen": True,
        "sms_opt_in": True,
        "submit_date": "04/15/2020",
        "month_of_birth": "05",
        "day_of_birth": "10",
        "year_of_birth": "1992",
        "state_id_number": TEST_BALLOT_REQUEST_STATE_ID_NUMBER,
        "is_18_or_over": TEST_BALLOT_REQUEST_IS_18_OR_OVER,
        "middle_initial": "S",
        "full_name": "some_first_name some_middle_name some_last_name",
        "county": addr.office.region.county,
        "region": addr.office.region.name,
        "address1_2": "some addr 1 some addr 2",
        "address_1_2_city": "some addr 1 some addr 2, some city",
        "address_city_state_zip": f"some city, {state.code} 12345",
        "full_address": f"some addr 1 some addr 2 some city, {state.code} 12345",
        "has_mailing_address": True,
        "mailing_address1_2": "some mailing addr some mailing addr 2",
        "mailing_city_state_zip": f"some mailing city, {state.code} 67890",
        "mailing_full_address": f"some mailing addr some mailing addr 2 some mailing city, {state.code} 67890",
        "mailto": ABSENTEE_BALLOT_MAILING_ADDRESS,
        "mailto_address1": addr.address,
        "mailto_address2": addr.address2,
        "mailto_address3": addr.address3,
        "mailto_city_state_zip": ABSENTEE_BALLOT_MAILING_CITY_STATE_ZIP,
        "leo_contact_info": f"Email: {addr.email}\nPhone: {addr.phone}",
        "vbm_deadline": "foo deadline",
        "vbm_first_day_to_apply": "bar date",
    }

    return (ballot_request, expected_data)


def get_filled_slugs() -> List[str]:
    _, record_filled_fields = make_test_data()
    record_slugs = list(record_filled_fields.keys())

    return record_slugs + ["signature", "same_mailing_address"]