import React from 'react';

import AdapterEndpoint from "./odin_control";

import AegirNavbar from './components/AegirNavbar';
import AegirStatus from './components/AegirStatus';

import './App.css';

const App = () =>{

  const aegir_endpoint = new AdapterEndpoint("aegir", process.env.REACT_APP_ENDPOINT_URL);

  return (
    <div className="aegir">
      <h1>AEGIR</h1>
      <AegirNavbar />
      <AegirStatus endpoint={aegir_endpoint} />
    </div>
  );
};

export default App;
