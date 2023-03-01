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

const AegirApp = (props) => {

  const { endpoint_url } = props;

  const endpoint = useAdapterEndpoint("aegir", endpoint_url, {interval: 500});

  const setError = useErrorOutlet();
  useEffect(() => {
    setError(endpoint.error);
  }, [endpoint.error, setError]);

  return (
    <div className="aegir">
      <AegirNavbar />
      <AegirErrorOutlet />
      <Container fluid>
        <Row>
          <Col>
            <AegirControl endpoint={endpoint} />
          </Col>
          <Col>
            <AegirSystemStatus state={endpoint.data} />
          </Col>
        </Row>
        <Row>
          <Col>
            <AegirFrontendStatus state={endpoint.data} />
          </Col>
          <Col>
            <AegirLinkStatus state={endpoint.data} />
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default AegirApp;
