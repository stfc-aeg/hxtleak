"""Event logger for the Hxtleak adapter.

This module implements a simple event logger for the Hxtleak adapter. It implements the standard
logging module method (e.g. debug(), info(), warning()), with log messages being emitted to the
specified logger but also captured in a local queue of fixed depth, which can then be exposed
by an adapter parameter tree for clients to retrieve. Events after a specified timestamp can be
retrieved, minimising traffic and load to the client.

Tim Nicholls, STFC Detector Systems Software Group
"""
import logging

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from functools import partial


@dataclass
class LogEvent:
    """Log event dataclass."""

    timestamp: datetime
    level: int
    message: str


class HxtleakEventLogger():
    """Hxtleak event logger class."""

    TIMESTAMP_FORMAT = "%d/%m/%y %X.%f"

    def __init__(self, logger=None, maxlen=250):
        """Intialise the event logger.

        This method initialises the event logger, binding to the specified logger instance and
        setting up an event storage queue of the specified depth.

        :param logger: system logger instance to bind to. If None, bind to the root logger
        :param maxlen: maximum length of the event storage queue (default = 250)
        """
        # If no logger specified, bind to the root logger instance
        if not logger:
            logger = logging.getLogger()
        self.logger = logger

        # Set up the event queue and internal variables
        self._deque = deque(maxlen=maxlen)
        self._events = []
        self._last_timestamp = None
        self._events_since = None

        # Generate logging convenience methods (e.g. debug(), info(), ...) which mirror the
        # standard logger
        for level in (
            logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
        ):
            setattr(self, logging.getLevelName(level).lower(), partial(self.log, level))

    def log(self, level, msg, *args, **kwargs):
        """Log a message to the event log.

        This method logs an event to the event log. If the underlying logger is enabled for the
        specifed logging, a log event is created and queued and the event passed on to the
        underlying logger.

        :param level: log level for event (e.g. DEBUG, INFO, ...)
        :param msg: event message log log
        :param *args: positiional logging arguments
        :param **kwargs: additional keyword arguments to pass to the logger
        """
        # If logging enabled for the specified level, create and queue a log event and pass to
        # the underlying logger.
        if self.logger.isEnabledFor(level):

            # Log the message to the underlying logger
            self.logger.log(level, msg, *args, **kwargs)

            # Construct a log event for the current message
            timestamp = datetime.now()
            msg = str(msg)
            if args:
                msg = msg % args
            self._deque.append(LogEvent(timestamp, level, msg))

            # Update the last timestamp record in the event logger
            self._last_timestamp = timestamp

    def events(self):
        """Return logged events.

        This method returns logged events in a dict format amenable to serialisation for use by a
        client. The events returned are from the list populated by the most recent call to
        set_events_since(), i.e. after a specified time

        :return list of dict-formatted events since the set_events_since() timestamp
        """
        return [
            {
                "timestamp": datetime.strftime(event.timestamp, self.TIMESTAMP_FORMAT),
                "level": logging.getLevelName(event.level),
                "message": event.message
            }
            for event in self._events
        ]

    def last_timestamp(self):
        """Return the last event timetamp.

        This method returns the timestamp of the most recent event logged.

        :return: timestamp of last event logged as ISO-formatted string
        """
        return datetime.strftime(
            self._last_timestamp, self.TIMESTAMP_FORMAT
        ) if self._last_timestamp else ''

    def events_since(self):
        """Return the currently set timestamp for retrieving events since.

        This method returns the current valye of the "events since" timestamp, which is used by
        clients to specifiy which logged events to return.

        :return: current events-since timestamp as ISO-formatted string
        """
        return datetime.strftime(
            self._events_since, self.TIMESTAMP_FORMAT
        ) if self._events_since else ''

    def set_events_since(self, events_since_str=None):
        """Set the timestamp for retrieving events since.

        This method sets the events since timestamp, which determines which events will be returned
        based on the specified timestamp. If no timestamp is specified, all logged events will be
        added to the list. The internal event list is updated by this call, which is then retreieved
        by a subsequent call to events().

        :param events_since_str: ISO-formatted string specifying timestamp to get events since
        """
        # Create an empty event list to populate
        events = []

        # Copy the event queue into a working list so that events aren't removed from it
        event_list = list(self._deque)

        # If a timestamp was specified, parse that and populate the event list with events logged
        # since that timestamp. Otherwise populate the event list with all logged events still
        # in the queue.
        if events_since_str:

            self._events_since = datetime.strptime(events_since_str, self.TIMESTAMP_FORMAT)

            for index, event in enumerate(event_list):
                if event.timestamp > self._events_since:
                    events = event_list[index:]
                    break
        else:
            events = event_list

        self._events = events
