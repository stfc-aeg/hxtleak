import React, { useState, useEffect } from "react";
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';

const StatusLine = ({ name, value, unit }) => (
  <p>{name}:&nbsp;{value}{unit}</p>
);

const StatusCard = ({ title, data }) => (
  <Card>
    <Card.Header as="b">{title}</Card.Header>
    <Card.Body>
      {data.map(d => (<StatusLine key={d.name} name={d.name} value={d.value} unit={d.unit} />))}
    </Card.Body>
  </Card>
)

const AegirStatus = ({ endpoint }) => {

  const [aegir_status, updateStatus] = useState(null);

  useEffect(() => {
    const timer_id = setInterval(() => {
        endpoint.get("")
        .then(result => {
          updateStatus(result);
        })
        .catch(error => {
          console.log(error.message);
        });
    }, 1000);
    return () => {
      clearInterval(timer_id);
    }
  }, [endpoint]);

  const env_status = aegir_status ? [
    {name: "Temperature", value: aegir_status.packet_info.temp.toFixed(1), unit: "°C"},
    {name: "Humidity", value: aegir_status.packet_info.humidity.toFixed(1), unit: "%"},
    {name: "Probe1", value: aegir_status.packet_info.probe1.toFixed(1), unit: "°C"},
    {name: "Probe2", value: aegir_status.packet_info.probe2.toFixed(1), unit: "°C"},
    {name: "Fault", value: aegir_status.packet_info.fault.toString(), unit: ""},
  ] : [] ;

  const rx_status = aegir_status ? [
    {name: "Current status", value: aegir_status.status, unit: ""},
    {name: "Packets received", value: aegir_status.good_packets, unit: ""},
    {name: "Packet errors", value: aegir_status.bad_packets, unit: ""},
    {name: "Last packet received", value: aegir_status.time_received, unit: ""},
  ] : [] ;

  return (
    <Row>
      <Col>
        <StatusCard title="ENV" data={env_status} />
      </Col>
      <Col>
        <StatusCard title="RX" data={rx_status} />
      </Col>
    </Row>
  );
}

export default AegirStatus;
