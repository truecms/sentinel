import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from './ErrorBoundary';

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  const originalError = console.error;
  beforeAll(() => {
    console.error = vi.fn();
  });

  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText("We're sorry for the inconvenience. Please try refreshing the page.")).toBeInTheDocument();
  });

  it('shows refresh page button', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );
    
    const refreshButton = screen.getByText('Refresh Page');
    expect(refreshButton).toBeInTheDocument();
  });

  it('shows try again button that resets error state', async () => {
    const user = userEvent.setup();
    
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    const tryAgainButton = screen.getByText('Try Again');
    await user.click(tryAgainButton);
    
    // Rerender with non-throwing component
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('calls console.error when catching an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow />
      </ErrorBoundary>
    );
    
    expect(console.error).toHaveBeenCalled();
  });
});