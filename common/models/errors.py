class ModelError(Exception):
    """
    Raised for unexpected/unintended behaviors
    related to XNAT Models.
    """


class ValidatorExists(ModelError):
    """
    Raised when a validator already exists in the
    model's validators.
    """


class NotAValidator(ModelError):
    """
    Raised when an object does not qualify as a
    Validator.
    """
