import React, { useEffect } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import { useAdapterEndpoint } from './AdapterEndpoint';

import { AegirErrorOutlet, useErrorOutlet } from './AegirErrorContext';
import AegirNavbar from './AegirNavbar';
import AegirControl from './AegirControl';
import AegirSystemStatus from './AegirSystemStatus';
import AegirFrontendStatus from './AegirFrontendStatus';
import AegirLinkStatus from './AegirLinkStatus';
import AegirEventLog from './AegirEventLog';

const AegirApp = (props) => {

  const { endpoint_url } = props;

  const system_endpoint = useAdapterEndpoint("aegir/system", endpoint_url, {interval: 500});
  const event_endpoint = useAdapterEndpoint("aegir/event_log", endpoint_url, {});

  const state = system_endpoint.data ? system_endpoint.data.system : null;

  const setError = useErrorOutlet();
  useEffect(() => {
    setError(system_endpoint.error);
  }, [system_endpoint.error, setError]);

  return (
    <div className="aegir">
      <AegirNavbar />
      <AegirErrorOutlet />
      <Container fluid>
        <Row>
          <Col>
            <AegirControl endpoint={system_endpoint} />
          </Col>
          <Col>
            <AegirSystemStatus state={state} />
          </Col>
        </Row>
        <Row>
          <Col>
            <AegirFrontendStatus state={state} />
          </Col>
          <Col>
            <AegirLinkStatus state={state} />
          </Col>
        </Row>
        <Row>
          <Col>
            <AegirEventLog endpoint={event_endpoint} />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default AegirApp;
