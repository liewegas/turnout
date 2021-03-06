from django.db import models
from enumfields import EnumField
from phonenumber_field.modelfields import PhoneNumberField

from action.mixin_models import ActionModel
from common import enums
from common.utils.models import TimestampModel, TrackingModel, UUIDModel
from common.validators import zip_validator
from multi_tenant.mixins_models import PartnerModel


class BallotRequest(
    ActionModel, PartnerModel, TrackingModel, UUIDModel, TimestampModel
):
    first_name = models.TextField(null=True)
    middle_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True)
    suffix = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    email = models.EmailField(null=True)
    phone = PhoneNumberField(null=True, blank=True)
    address1 = models.TextField(null=True)
    address2 = models.TextField(null=True, blank=True)
    city = models.TextField(null=True)
    state = models.ForeignKey(
        "election.State",
        on_delete=models.PROTECT,
        related_name="absentee_primary",
        null=True,
    )
    zipcode = models.TextField(null=True, validators=[zip_validator])

    mailing_address1 = models.TextField(null=True, blank=True)
    mailing_address2 = models.TextField(null=True, blank=True)
    mailing_city = models.TextField(null=True, blank=True)
    mailing_state = models.ForeignKey(
        "election.State",
        on_delete=models.PROTECT,
        related_name="absentee_mailing",
        null=True,
    )
    mailing_zipcode = models.TextField(
        null=True, validators=[zip_validator], blank=True
    )

    us_citizen = models.BooleanField(null=True, default=False)
    sms_opt_in = models.BooleanField(null=True, default=False)

    status = EnumField(
        enums.TurnoutActionStatus, default=enums.TurnoutActionStatus.PENDING, null=True,
    )

    region = models.ForeignKey("official.Region", null=True, on_delete=models.SET_NULL)

    result_item = models.ForeignKey(
        "storage.StorageItem", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ballot Request - {self.first_name} {self.last_name}, {self.state.pk}".strip()
