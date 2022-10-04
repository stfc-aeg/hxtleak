import React from 'react';
import StatusCard from './StatusCard';
import { ParameterTable, ParameterEntry } from './ParameterTable';

const AegirLinkStatus = ({ state }) => {

  const link_status = state ? [
    {name: "Receive status", value: state.status},
    {name: "Packets decoded", value: state.good_packets},
    {name: "Packet errors", value: state.bad_packets},
    {name: "Last receive", value: state.time_received},
  ] : [] ;

  return (
    <StatusCard title="Link status">
      <ParameterTable header={false} unit={false} widths={{ value: "75%"}}>
        {link_status.map((param) => (
          <ParameterEntry key={param.name} name={param.name} value={param.value} />
        ))}
      </ParameterTable>
    </StatusCard>
  );
}

export default AegirLinkStatus;
