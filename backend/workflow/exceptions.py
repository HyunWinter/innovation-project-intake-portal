"""Workflow errors
The API maps each errors to an HTTP status (400/403/404/409).
"""


class TransitionError(Exception):
    """Base class"""


class UnknownAction(TransitionError):
    """Error 404: Unregistered error"""


class RoleNotAllowed(TransitionError):
    """Error 403: User unauthorized"""


class IllegalTransition(TransitionError):
    """Error 409: Illegal action"""


class MissingFields(TransitionError):
    """Error 400: Missing one or more payload"""

    def __init__(self, fields):
        self.fields = list(fields)
        super().__init__("Missing required fields: " + ", ".join(self.fields))
