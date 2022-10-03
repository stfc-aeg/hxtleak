import React, { useState, useEffect} from 'react';
import ControlSwitch from './ControlSwitch';

const StateControlSwitch = (props) => {

  const {title, disabled, endpoint, state: defaultState, path: defaultPath } = props;

  const [state, setState] = useState(defaultState);
  const [path, setPath] = useState();
  const [param, setParam] = useState();

  useEffect(() => {
    setState(defaultState);
  }, [defaultState]);

  useEffect(() => {
    let [_path, _param] = defaultPath.split(/\/(?!.*\/)(.*)/, 2);
    setParam(_param);
    setPath(_path);
  }, [defaultPath]);

  const onChange = (value) => {
    endpoint.put({ [param]: value}, path)
    .then(result => {
      setState(result[param])
    })
    .catch(error => {
      console.log(error.message);
    });
  }

  return (
    <div>
      <ControlSwitch width="100px" title={title} id={title} disabled={disabled} onChange={onChange} checked={state} />
    </div>
  );
}

export default StateControlSwitch;