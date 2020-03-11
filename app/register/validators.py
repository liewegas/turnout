import logging

from rest_framework import serializers

logger = logging.getLogger("register")


class RegistrationValidator:
    requires_context = True

    def __call__(self, data, serializer):
        # This is an example of a custom validator, perhaps one that validates state info
        logger.info("Example Validator 1")
        logger.info(serializer.incomplete)
        logger.info(data)
        # raise serializers.ValidationError("Invalid Registration")


class AddressValidator:
    requires_context = True

    def __call__(self, data, serializer):
        # This is another example of a validator, perhaps one that validates addresses
        logger.info("Example Validator 2")
        logger.info(serializer.incomplete)
        logger.info(data)
        # raise serializers.ValidationError("Invalid Address")
