import React, { useEffect } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import { useAdapterEndpoint } from './AdapterEndpoint';

import { HxtleakErrorOutlet, useErrorOutlet } from './HxtleakErrorContext';
import HxtleakNavbar from './HxtleakNavbar';
import HxtleakControl from './HxtleakControl';
import HxtleakSystemStatus from './HxtleakSystemStatus';
import HxtleakFrontendStatus from './HxtleakFrontendStatus';
import HxtleakLinkStatus from './HxtleakLinkStatus';
import HxtleakEventLog from './HxtleakEventLog';

const HxtleakApp = (props) => {

  const { endpoint_url } = props;

  const system_endpoint = useAdapterEndpoint("hxtleak/system", endpoint_url, {interval: 500});
  const event_endpoint = useAdapterEndpoint("hxtleak/event_log", endpoint_url, {});

  const state = system_endpoint.data ? system_endpoint.data.system : null;

  const setError = useErrorOutlet();
  useEffect(() => {
    setError(system_endpoint.error);
  }, [system_endpoint.error, setError]);

  return (
    <div className="hxtleak">
      <HxtleakNavbar />
      <HxtleakErrorOutlet />
      <Container fluid>
        <Row>
          <Col>
            <HxtleakControl endpoint={system_endpoint} />
          </Col>
          <Col>
            <HxtleakSystemStatus state={state} />
          </Col>
        </Row>
        <Row>
          <Col>
            <HxtleakFrontendStatus state={state} />
          </Col>
          <Col>
            <HxtleakLinkStatus state={state} />
          </Col>
        </Row>
        <Row>
          <Col>
            <HxtleakEventLog endpoint={event_endpoint} />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default HxtleakApp;
