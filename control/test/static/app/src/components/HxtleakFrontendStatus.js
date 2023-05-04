import React from 'react';

import StatusCard from './StatusCard';
import {ParameterTable, ParameterEntry} from './ParameterTable';

const statusString = (value) => {
  return "0x" + value.toString(16).toUpperCase();
}

const HxtleakFrontendStatus = ({ state }) => {

  const fe_status = (state && state.packet_info) ? [
    {
      name: "Board temperature", value: state.packet_info.board_temp.toFixed(1),
      threshold: state.packet_info.board_temp_threshold.toFixed(1), unit: "°C"
    },
    {
      name: "Board humidity", value: state.packet_info.board_humidity.toFixed(1),
      threshold: state.packet_info.board_humidity_threshold.toFixed(1), unit: "%"
    },
    {
      name: "Temperature probe 1", value: state.packet_info.probe_temp_1.toFixed(1),
      threshold: state.packet_info.probe_temp_1_threshold.toFixed(1), unit: "°C"
    },
    {
      name: "Temperature probe 2", value: state.packet_info.probe_temp_2.toFixed(1),
      threshold: state.packet_info.probe_temp_2_threshold.toFixed(1), unit: "°C"
    },
    {
      name: "Leak continuity", value: state.packet_info.cont ? "OK" : "Error",
      threshold: "-", unit: "-"
    },
    {
      name: "Leak detected", value: state.packet_info.leak_detected ? "Yes" : "No",
      threshold: "-", unit: "-"
    },
    {
      name: "Fault", value: state.packet_info.fault ? "Yes" : "No",
      threshold: "-", unit: "-"
    },
    {
      name: "Warning", value: state.packet_info.warning ? "Yes" : "No",
      threshold: "-", unit: "-"
    },
    {
      name: "Sensor status", value: statusString(state.packet_info.sensor_status),
      threshold: "-", unit: "-"
    }
  ] : [] ;

  const columns = {
    "name": "Parameter",
    "value": "Value",
    "threshold": "Threshold",
    "unit": "Unit"
  };

  const col_widths = {
    "name": "55%",
    "value": "15%",
    "threshold": "15%",
    "unit": "15%"
  };

  return (
    <StatusCard title="Frontend sensors">
      <ParameterTable columns={columns} widths={col_widths}>
          {fe_status.map((param) => (
            <ParameterEntry key={param.name} param={param} />
          ))}
      </ParameterTable>
    </StatusCard>
  );
}

export default HxtleakFrontendStatus;
