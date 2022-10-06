import React, { useState, useEffect, useMemo } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import AdapterEndpoint from '../odin_control';

import { AegirErrorOutlet, useErrorOutlet } from './AegirErrorContext';
import AegirNavbar from './AegirNavbar';
import AegirControl from './AegirControl';
import AegirSystemStatus from './AegirSystemStatus';
import AegirFrontendStatus from './AegirFrontendStatus';
import AegirLinkStatus from './AegirLinkStatus';

const AegirApp = (props) => {

  const { endpoint_url } = props;

  const endpoint = useMemo(() => new AdapterEndpoint("aegir", endpoint_url), [endpoint_url]);
  const setError = useErrorOutlet();

  const [state, updateState] = useState(null);

  useEffect(() => {

    const timer_id = setInterval(() => {
      endpoint.get("")
      .then(result => {
        updateState(result);
      })
      .catch(error => {
        setError(error);
      });

    }, 500);
    return () => {
      clearInterval(timer_id);
    }
  }, [endpoint, setError]);

  return (
    <div className="aegir">
      <AegirNavbar />
      <AegirErrorOutlet />
      <Container fluid>
        <Row>
          <Col>
            <AegirControl endpoint={endpoint} state={state} />
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
      </Container>
    </div>
  );
};

export default AegirApp;
