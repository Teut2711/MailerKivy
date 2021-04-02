
class InvalidSystemIDError(Exception):
    """Exception raised if license key used on another system."""

    def __init__(
        self, message="This key is not made for this system. Contact the dealer."
    ):

        super().__init__(message)


class RegistrationTimeExpiredError(Exception):
    """Exception raised if registration time is expired."""

    def __init__(
        self,
        message="Registration time is expired. Contact the dealer and ask for another key.",
    ):
        self.message = message
        super().__init__(message)



class LicenseKeyExpiredError(Exception):
    """Exception raised if registration time is expired."""

    def __init__(self, message="License key is expired. Buy a new one."):
        self.message = message
        super().__init__(message)

