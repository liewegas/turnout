from django.core.management.base import BaseCommand

from absentee.generateform import prepare_absentee_request_form


class Command(BaseCommand):
    help = "Generate an absentee ballot request"
    requires_system_checks = False

    def handle(self, *args, **options):
        storage_item = prepare_absentee_request_form(
            region_external_id=431101,
            state_code="MA",
            last_name="Weissmann",
            email="ben@voteamerica.com",
            partner=None,
        )

        print(storage_item.download_url)
