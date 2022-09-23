import React from 'react';
import { render, screen } from '@testing-library/react';

import App from './App';

test('renders top-level app component', () => {
  render(<App />);
  const aegir_element = screen.getAllByText(/AEGIR/);
  expect(aegir_element.length > 0).toBeTruthy();
});
