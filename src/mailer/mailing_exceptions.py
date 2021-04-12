class SubjectMissingError(Exception):
    """Exception raised if subject is missing."""

    def __init__(
        self,
        row_num,
        message="Subject is Missing.Mail can't be send to row number ",
    ):
        message = message + " " + str(row_num + 1)
        super().__init__(message)

class FromMissingError(Exception):
    """Exception raised if from is missing."""

    def __init__(
        self,
        row_num,
        message="From is Missing.Mail can't be send to row number ",
    ):
        message = message + " " + str(row_num + 1)
        super().__init__(message)
