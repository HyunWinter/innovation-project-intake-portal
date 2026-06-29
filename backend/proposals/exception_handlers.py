"""Map workflow errors to HTTP responses

The state machine raises TransitionError subclasses
The API turns each into its status code
"""

from rest_framework.response import Response
from rest_framework.views import exception_handler

from workflow.exceptions import (
    IllegalTransition,
    MissingFields,
    RoleNotAllowed,
    TransitionError,
    UnknownAction,
)

# Error mapping
_STATUS = [
    (UnknownAction, 404),
    (RoleNotAllowed, 403),
    (IllegalTransition, 409),
    (MissingFields, 400),
]


def api_exception_handler(exc, context):
    if isinstance(exc, TransitionError):
        status_code = next((code for cls, code in _STATUS if isinstance(exc, cls)), 400)
        body = {"detail": str(exc)}
        if isinstance(exc, MissingFields):
            body["fields"] = exc.fields
        return Response(body, status=status_code)
    return exception_handler(exc, context)
