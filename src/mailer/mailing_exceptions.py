class SubjectMissingError(Exception):
    """Exception raised if subject is missing."""

    def __init__(
        self,
        message="Subject is Missing.",
    ):

        super().__init__(message)


class FromMissingError(Exception):
    """Exception raised if from is missing."""

    def __init__(
        self,
        message="From is Missing.",
    ):
        super().__init__(message)
