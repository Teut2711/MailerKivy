class ToError(Exception):
    """Exception raised if to is invalid."""

    def __init__(
        self,
        message="Invalid `To`",
    ):

        super().__init__(message)


class SubjectError(Exception):
    """Exception raised if subject is invalid."""

    def __init__(
        self,
        message="Invalid `Subject`",
    ):

        super().__init__(message)


class FromError(Exception):
    """Exception raised if from is invalid."""

    def __init__(
        self,
        message="Invalid `From`.",
    ):
        super().__init__(message)
