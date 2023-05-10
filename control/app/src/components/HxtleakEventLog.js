import { useState, useEffect, useCallback, useRef } from 'react';

import StatusCard from './StatusCard';

const HxtleakEventLog = ({ endpoint }) => {

  const interval = 1000;

  const [events, setEvents] = useState(
    endpoint.data ? endpoint.data.event_log.events : []
  );

  const [events_since, setEventsSince] = useState(
    endpoint.data ? endpoint.data.event_log.events_since : ''
  );

  const [last_timestamp, setLastTimestamp] = useState(
    endpoint.data ? endpoint.data.event_log.last_timestamp : ""
  );

  const updateEvents = useCallback(() => {

    endpoint.put({"events_since" : last_timestamp})
    .then(result => {
        setLastTimestamp(result.event_log.last_timestamp);
        setEventsSince(result.event_log.events_since);
        if (result.event_log.events.length) {
            setEvents(old_events => [...old_events, ...result.event_log.events]);
        }
    })
    .catch(error => {
        console.log(error.message);
    })

  }, [events_since, last_timestamp, events]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    let timer_id = null;
    if (interval) {
        timer_id = setInterval(updateEvents, interval);
    }
    return () => {
        if (timer_id) {
            clearInterval(timer_id);
        }
    }

  }, [interval, updateEvents]);

  const scrollRef = useRef(null);
  const scrollEvents = () => {
    scrollRef.current.scrollTop = scrollRef.current?.scrollHeight;
  }

  useEffect(() => {
    scrollEvents();
  }, [events]);

  const renderEvent = (event) => {

    const event_level_class = "log-" + event.level.toLowerCase();

    return (
        <div key={event.timestamp} className={event_level_class}>
            {event.timestamp} : {event.level} : {event.message}<br/>
        </div>
    )
  }

  return (
    <StatusCard title="Event log">
      <pre ref={scrollRef} className="pre-scrollable">
        {events.map((event) => (
          renderEvent(event)
        ))}
      </pre>
    </StatusCard>
  )
}

export default HxtleakEventLog;
