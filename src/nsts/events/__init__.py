"""
Implementation of Publisher/Subscriber pattern for event
notification.

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
"""


class Notification(object):
    """
    Object that is passed to subscribers when
    they are notified about an event.
    """
    def __init__(self, event_name, sender, extra):
        self.event_name = event_name
        self.sender = sender
        self.extra = extra


class Dispatcher(dict):
    """
    Event dispatcher implements a central
    point for subscribers to connect and
    publisher to send notifications.
    """

    def connect(self, event_name, callback):
        """
        Connect a subscriber at an event.
        @param event_name The name of the event
        @param callback The callback to be called on publishing.
        """
        if event_name not in self:
            self[event_name] = []
        self[event_name].append(callback)

    def send(self, event_name, sender=None, **kwargs):
        """
        Send a notification to all subscribers of this
        event.
        @param event_name The name of the event
        @param sender The sender of this notification
        All extra parameters are passed directly to the notification
        object.
        """
        if event_name not in self:
            return

        n = Notification(event_name=event_name, sender=sender, extra=kwargs)
        for callback in self[event_name]:
            callback(n)

dispatcher = Dispatcher()
