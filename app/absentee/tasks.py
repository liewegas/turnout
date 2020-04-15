from celery import shared_task

from common.analytics import statsd


@shared_task
@statsd.timed("turnout.absentee.process_ballotrequest_submission")
def process_ballotrequest_submission(
    ballotrequest_pk: str, state_id_number: str, is_18_or_over: bool
) -> None:
    from .models import BallotRequest
    from .generateform import process_ballot_request

    ballot_request = BallotRequest.objects.select_related().get(pk=ballotrequest_pk)
    process_ballot_request(ballot_request)
