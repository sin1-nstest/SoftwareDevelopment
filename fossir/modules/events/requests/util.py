

from __future__ import unicode_literals

from fossir.core import signals
from fossir.util.signals import named_objects_from_signal


def get_request_definitions():
    """Returns a dict of request definitions"""
    return named_objects_from_signal(signals.plugin.get_event_request_definitions.send(), plugin_attr='plugin')


def is_request_manager(user):
    """Checks if the user manages any request types"""
    if not user:
        return False
    return any(def_.can_be_managed(user) for def_ in get_request_definitions().itervalues())
