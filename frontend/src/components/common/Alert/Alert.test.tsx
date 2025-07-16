import React from 'react';
import { render, screen } from '@testing-library/react';
import { Alert } from './Alert';

describe('Alert', () => {
  it('renders with title', () => {
    render(<Alert type="info" title="Test Alert" />);
    expect(screen.getByText('Test Alert')).toBeInTheDocument();
  });

  it('renders with message', () => {
    render(<Alert type="info" title="Test Alert" message="This is a test message" />);
    expect(screen.getByText('This is a test message')).toBeInTheDocument();
  });
});