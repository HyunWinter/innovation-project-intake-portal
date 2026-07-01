"""Custom Django signal for workflow events.

Sent after every workflow event
"""

import django.dispatch

# (request_obj, action, from_status, to_status, actor)
post_transition = django.dispatch.Signal()
