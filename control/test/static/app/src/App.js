import React from 'react';

import AegirErrorBoundary from './components/AegirErrorBoundary';
import AegirApp from './components/AegirApp';
import { AegirErrorContext } from './components/AegirErrorContext';

import './App.css';

const App = () =>{

  const endpoint_url = process.env.REACT_APP_ENDPOINT_URL;

  return (
    <div className="aegir">
      <AegirErrorBoundary>
        <AegirErrorContext>
          <AegirApp endpoint_url={endpoint_url} />
        </AegirErrorContext>
      </AegirErrorBoundary>
    </div>
  );
};

export default App;
