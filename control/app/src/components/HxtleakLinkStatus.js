import React from 'react';
import StatusCard from './StatusCard';
import { ParameterTable, ParameterEntry } from './ParameterTable';

const HxtleakLinkStatus = ({ state }) => {

  const link_status = state ? [
    {name: "Receive status", value: state.status},
    {name: "Packets decoded", value: state.good_packets},
    {name: "Packet errors", value: state.bad_packets},
    {name: "Last receive", value: state.time_received},
  ] : [] ;

  const columns = {
    "name": "Name",
    "value": "Value"
  }

  const col_widths = {
    "name": "25%",
    "value": "75%"
  }

  return (
    <StatusCard title="Link status">
      <ParameterTable columns={columns} header={false} unit={false} widths={col_widths}>
        {link_status.map((param) => (
          <ParameterEntry key={param.name} param={param} />
        ))}
      </ParameterTable>
    </StatusCard>
  );
}

export default HxtleakLinkStatus;
