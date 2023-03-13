import React from 'react';
import Table from 'react-bootstrap/Table';

const ParameterTableContext = React.createContext();

export const ParameterEntry = ({ param }) => {

    const ctx = React.useContext(ParameterTableContext);

    let col_styles = {};

    ctx.column_keys.forEach( (cell_name) => {
      col_styles[cell_name] = (cell_name in ctx.widths) ? { width : ctx.widths[cell_name]} : {};
    });

    return (
      <tr>
        {
          ctx.column_keys.map( (col_name) => (
            <td key={col_name} style={col_styles[col_name]}>{param[col_name]}</td>
          ))
        }
      </tr>
    );
}

export const ParameterTable = (props) => {

    const { columns = {}, header = true, widths = {} } = props;

    const column_keys = Object.keys(columns);

    const renderHeader = () => {
      return (
        <thead>
          <tr>
            {
              Object.entries(columns).map( ([col_key, col_name]) => (
                <th key={col_key}>{col_name}</th>
              ))
            }
          </tr>
        </thead>
      )
    }

    return (
        <Table striped hover>
        {header && renderHeader()}
        <tbody>
          <ParameterTableContext.Provider value={{ column_keys, widths }}>
            {props.children}
          </ParameterTableContext.Provider>
        </tbody>
      </Table>
    );
}
