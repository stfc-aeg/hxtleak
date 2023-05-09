import React from 'react';

import HxtleakErrorBoundary from './components/HxtleakErrorBoundary';
import HxtleakApp from './components/HxtleakApp';
import { HxtleakErrorContext } from './components/HxtleakErrorContext';

import './App.css';

const App = () =>{

  const endpoint_url = process.env.REACT_APP_ENDPOINT_URL;

  return (
    <div className="hxtleak">
      <HxtleakErrorBoundary>
        <HxtleakErrorContext>
          <HxtleakApp endpoint_url={endpoint_url} />
        </HxtleakErrorContext>
      </HxtleakErrorBoundary>
    </div>
  );
};

export default App;
