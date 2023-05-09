import React from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Alert from 'react-bootstrap/Alert';

import StatusCard from './StatusCard';

const HxtleakSystemStatus = (props) => {

  const {state} = props;

  const chiller_outlet_disabled = state ? !state.outlets.chiller.enabled : true;
  const chiller_outlet_state = state ? state.outlets.chiller.state : false;
  const daq_outlet_disabled = state ? !state.outlets.daq.enabled : true;
  const daq_outlet_state = state ? state.outlets.daq.state : false;

  const fault_state = state ? state.fault : true;
  const fault_variant = fault_state ? "danger" : "success";
  const fault_text = "Fault: " + (fault_state ? "yes" : "no");

  const warning_state = state ? state.warning : true;
  const warning_variant = warning_state ? "warning" : "success";
  const warning_text = "Warning: " + (warning_state ? "yes" : "no");

  const chiller_power_text = "Chiller: " + (
    chiller_outlet_disabled ? "disabled" : (
      chiller_outlet_state ? "on" : "off"
    )
  );
  const chiller_power_variant = chiller_outlet_state ? "success" : "warning";

  const daq_power_text = "DAQ: " + (
    daq_outlet_disabled ? "disabled" : (
      daq_outlet_state ? "on" : "off"
    )
  );
  const daq_power_variant = daq_outlet_state ? "success" : "warning";

  return (
    <StatusCard title="System status">
      <Row>
        <Col>
          <Alert key="fault" variant={fault_variant}>{fault_text}</Alert >
        </Col>
        <Col>
          <Alert key="warning" variant={warning_variant}>{warning_text}</Alert >
        </Col>
        <Col>
          <Alert key="chiller" variant={chiller_power_variant}>{chiller_power_text}</Alert>
        </Col>
        <Col>
          <Alert key="daq" variant={daq_power_variant}>{daq_power_text}</Alert>
        </Col>
      </Row>
    </StatusCard>
  )
}

export default HxtleakSystemStatus;