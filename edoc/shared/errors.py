class EdocError(Exception):
    """Base exception for edoc package."""


class SchemaValidationError(EdocError):
    pass


class TransportError(EdocError):
    pass


class SigningError(EdocError):
    pass
