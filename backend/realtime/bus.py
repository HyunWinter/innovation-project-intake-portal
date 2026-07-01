"""Event bus for SSE notification broadcasting

Methods:
    subscribe   Each SSE client registers a queue + user_id
    unsubscribe Remove an SSE client's queue
    publish     pushed only to queues whose user_id is in the event's
                target_user_ids set

This only for single-process deployment (single container docker).
For multi-process production, you might want something like a Redis Pub/Sub.
"""

import queue
import threading

_lock = threading.Lock()
# Maps queue -> user_id (str)
_subscribers: dict[queue.Queue, str] = {}


def subscribe(user_id):
    """Register a new SSE client with their user_id and return its event queue"""
    q = queue.Queue()
    with _lock:
        _subscribers[q] = str(user_id)
    return q


def unsubscribe(q):
    """Remove an SSE client's queue (called on disconnect)"""
    with _lock:
        _subscribers.pop(q, None)


def publish(event: dict):
    """Push an event only to targeted SSE clients"""
    target_ids = event.get("target_user_ids", set())
    user_to_notif_id = event.get("user_to_notif_id", {})

    with _lock:
        dead = []
        for q, user_id in _subscribers.items():
            # Only deliver to targeted users
            if user_id not in target_ids:
                continue

            try:
                # Customize the event for this specific user so they get their own DB ID
                user_event = dict(event)
                user_event["data"] = dict(event["data"])
                user_event["data"]["id"] = user_to_notif_id.get(user_id)
                q.put_nowait(user_event)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.pop(q, None)
