import React from 'react';
import Card from 'react-bootstrap/Card';

const StatusCard = (props) => (
  <Card className="status_card">
    <Card.Header as="b">
        {props.title}
    </Card.Header>
    <Card.Body>
      {props.children}
    </Card.Body>
  </Card>
)

export default StatusCard;