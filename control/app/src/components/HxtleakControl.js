import React from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import StatusCard from './StatusCard';
import StateControlSwitch from './StateControlSwitch';

const HxtleakControl = ({ endpoint }) => {

  const state = endpoint.data ? endpoint.data.system : null;

  const chiller_outlet_disabled = state ? !state.outlets.chiller.enabled : true;
  const chiller_outlet_state = state ? state.outlets.chiller.state : false;
  const daq_outlet_disabled = state ? !state.outlets.daq.enabled : true;
  const daq_outlet_state = state ? state.outlets.daq.state : false;

  return (
    <StatusCard title="Power control">
      <Row md="auto">
        <Col>
          <StateControlSwitch
            title="Chiller"
            disabled={chiller_outlet_disabled}
            state={chiller_outlet_state}
            endpoint={endpoint}
            path="outlets/chiller/state"
          />
        </Col>
        <Col>
          <StateControlSwitch
            title="DAQ"
            disabled={daq_outlet_disabled}
            state={daq_outlet_state}
            endpoint={endpoint}
            path="outlets/daq/state"
          />
        </Col>
      </Row>
    </StatusCard>
  )
}

export default HxtleakControl;