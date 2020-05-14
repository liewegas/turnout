from model_bakery.recipe import Recipe

from common import enums

from .models import StorageItem

registration_form = Recipe(
    StorageItem, app=enums.FileType.REGISTRATION_FORM, _create_files=True
)

ballot_request_form = Recipe(
    StorageItem, app=enums.FileType.ABSENTEE_REQUEST_FORM, _create_files=True
)
