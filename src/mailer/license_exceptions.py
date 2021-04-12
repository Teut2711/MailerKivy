class UserNotRegisteredError(Exception):
    """Exception raised if new user opens the software."""

    def __init__(
        self, message="Please enter the license key and token to register."
    ):
        super().__init__(message)


class InvalidCredentialsError(Exception):
    """Exception raised if invalid credentials."""

    def __init__(
        self, message="Not a valid license key or token.Contact the dealer."
    ):
        super().__init__(message)


class InvalidSystemIDError(Exception):
    """Exception raised if license key used on another system."""

    def __init__(
        self,
        message="This key is not made for this system. Contact the dealer.",
    ):

        super().__init__(message)


class RegistrationTimeExpiredError(Exception):
    """Exception raised if registration time is expired."""

    def __init__(
        self,
        message="Registration time is expired. Contact the dealer and ask for another key.",
    ):
        super().__init__(message)


class LicenseExpiredError(Exception):
    """Exception raised if registration time is expired."""

    def __init__(self, message="License key is expired. Buy a new one."):
        super().__init__(message)
