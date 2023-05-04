import React from 'react';
import { render, screen } from '@testing-library/react';

import App from './App';

test('renders top-level app component', () => {
  render(<App />);
  const hxtleak_element = screen.getAllByText(/HXTLEAK/);
  expect(hxtleak_element.length > 0).toBeTruthy();
});
