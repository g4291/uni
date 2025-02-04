#!/usr/bin/env python3

"""
uni.events.base

base events
"""

from __future__ import annotations
from typing import Any, List, Optional
import uuid
from typing import Any, Callable, Dict

from ..exceptions import BaseHTTPException
from ..logger import color_red, core_logger
from ..utils import timestamp_factory, id_factory


logger = core_logger().getChild("events")


# subscribers register
_subscribers: Dict[str, List[Callable[[Any], None]]] = dict()

class Event():
    """ Base Event class """
    def __init__(self, data: Any, event_id: Optional[uuid.UUID] = None, user_id: Optional[uuid.UUID] = None, model_name: Optional[str] = None) -> None:

        self._data = data
        self._timestamp = timestamp_factory()
        self._user_id = user_id

        if model_name: self._model_name = model_name
        else: self._model_name = None

        if not event_id: self._id = id_factory()
        else: self._id = event_id

    def publish(self) -> None:
        """Publish event."""
        # nothing to do
        if not self.__class__.__name__ in _subscribers:
            return None

        for s in _subscribers[self.__class__.__name__]:
            try:
                # call subscriber
                s(self)
            except BaseHTTPException:
                raise
            except Exception as e:
                logger.error(color_red(str(e)+ ", subscriber: "+ s.__name__))

    def _get_data(self) -> Any:
        """ anbstract method to get event data """
        return self._data
        
    @property
    def data(self):
        return self._get_data()
    
    @property
    def user_id(self):
        return self._user_id

    @property
    def data_model(self) -> Any:
        return self.data.__class__

    @property
    def model_name(self) -> str:
        if not self._model_name: return self.data_model.__name__
        return self._model_name

    @property
    def name(self) -> str:
        return self.__class__.__name__


class EventCreated(Event):
    """Event on create."""

class EventUpdated(Event):
    """Event on update."""

class EventDeleted(Event):
    """Event on delete."""

class EventSuccessLogin(Event):
    """Event on successfull login."""

class EventBadLogin(Event):
    """Event on bad login."""

class EventAPIRequest(Event):
    """Event on API request."""


if __name__ == "__main__": exit()
