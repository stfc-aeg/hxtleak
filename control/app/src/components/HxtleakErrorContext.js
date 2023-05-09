import React, { useState, useMemo, useRef, useEffect, useContext } from 'react';
import Alert from 'react-bootstrap/Alert';

const ErrorContext = React.createContext();

export const HxtleakErrorContext = (props) => {

  const [error, setError] = useState(null);
  const ctx = useMemo(() => ({ error, setError }), [error]);

  return <ErrorContext.Provider value={ctx}>
    {props.children}
  </ErrorContext.Provider>

}

export const HxtleakErrorInlet = ({ error }) => {

    const ref = useRef();
    const errorContext = useContext(ErrorContext);

    useEffect(() => {
      if (errorContext === ref.current) {
        // This render has not been triggered via the context
        errorContext.setError(error)
      } else {
        ref.current = errorContext
      }
    });
    return null;
  }
export const HxtleakErrorOutlet = () => {

  const { error, setError } = useContext(ErrorContext);

  return (
    error && (
        <Alert variant='danger' onClose={() => setError(null)} dismissible>
            {error.message}
        </Alert>
    )
  )
}

export const useErrorOutlet = () => {
    const errorCtx = useContext(ErrorContext);
    return errorCtx.setError;
}
