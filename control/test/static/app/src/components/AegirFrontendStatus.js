import React from 'react';

import StatusCard from './StatusCard';
import {ParameterTable, ParameterEntry} from './ParameterTable';

const AegirFrontendStatus = ({ state }) => {

  const env_status = state ? [
    {name: "Board Temperature", value: state.packet_info.temp.toFixed(1), unit: "°C"},
    {name: "Humidity", value: state.packet_info.humidity.toFixed(1), unit: "%"},
    {name: "Temperature Probe 1", value: state.packet_info.probe1.toFixed(1), unit: "°C"},
    {name: "Temperature Probe 2", value: state.packet_info.probe2.toFixed(1), unit: "°C"},
    {name: "Leak continuity", value: state.packet_info.cont ? "OK" : "Error", unit: "-"},
    {name: "Leak detected", value: state.packet_info.leak_detected ? "Yes" : "No", unit: "-"},
    {name: "Fault", value: state.packet_info.fault ? "Yes" : "No", unit: "-"},
  ] : [] ;

  return (
    <StatusCard title="Frontend sensors">
      <ParameterTable>
          {env_status.map((param) => (
            <ParameterEntry key={param.name} name={param.name} value={param.value} unit={param.unit} />
          ))}
      </ParameterTable>
    </StatusCard>
  );
}

export default AegirFrontendStatus;
