import React, { useState, useEffect } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


import AdapterEndpoint from './odin_control';

import AegirNavbar from './components/AegirNavbar';
import AegirControl from './components/AegirControl';
import AegirSystemStatus from './components/AegirSystemStatus';
import AegirFrontendStatus from './components/AegirFrontendStatus';
import AegirLinkStatus from './components/AegirLinkStatus';

import './App.css';

const App = () =>{

  const endpoint = new AdapterEndpoint("aegir", process.env.REACT_APP_ENDPOINT_URL);
  const [state, updateState] = useState(null);

  const doUpdate = () => {
    endpoint.get("")
    .then(result => {
      updateState(result);
    })
    .catch(error => {
      console.log(error.message);
    });
  }

  useEffect(() => {
    doUpdate();
    const timer_id = setInterval(doUpdate, 1000);
    return () => {
      clearInterval(timer_id);
    }
  }, []);

  return (
    <div className="aegir">
      <AegirNavbar />
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

export default App;
