from celery import shared_task

from common.analytics import statsd
from common.enums import TurnoutActionStatus


@shared_task
@statsd.timed("turnout.register.process_registration_submission")
def process_registration_submission(
    registration_pk: str, state_id_number: str, is_18_or_over: bool
) -> None:
    from .models import Registration
    from .generateform import process_registration

    registration = Registration.objects.select_related().get(pk=registration_pk)
    process_registration(registration, state_id_number, is_18_or_over)


@shared_task
@statsd.timed("turnout.register.send_registration_notification")
def send_registration_notification(registration_pk: str) -> None:
    from .models import Registration
    from .notification import trigger_notification

    registration = Registration.objects.select_related().get(pk=registration_pk)
    registration.status = TurnoutActionStatus.PDF_SENT
    registration.save(update_fields=["status"])

    trigger_notification(registration)
