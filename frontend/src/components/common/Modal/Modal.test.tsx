import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from './Modal';
import { Button } from '../Button';

describe('Modal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    title: 'Test Modal',
    children: <div>Modal content</div>
  };

  it('renders when open', () => {
    render(<Modal {...defaultProps} />);
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
  });

  it('renders with description', () => {
    render(
      <Modal {...defaultProps} description="This is a test modal description" />
    );
    expect(screen.getByText('This is a test modal description')).toBeInTheDocument();
  });

  it('renders with actions', () => {
    render(
      <Modal
        {...defaultProps}
        actions={
          <>
            <Button variant="secondary">Cancel</Button>
            <Button>Confirm</Button>
          </>
        }
      />
    );
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Confirm')).toBeInTheDocument();
  });

  it('calls onClose when clicking backdrop', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    
    render(<Modal {...defaultProps} onClose={onClose} />);
    
    // Click on the backdrop (outside the modal panel)
    const backdrop = screen.getByRole('dialog').parentElement;
    if (backdrop) {
      await user.click(backdrop);
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    }
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<Modal {...defaultProps} size="sm" />);
    let panel = screen.getByRole('dialog');
    expect(panel).toHaveClass('max-w-md');

    rerender(<Modal {...defaultProps} size="lg" />);
    panel = screen.getByRole('dialog');
    expect(panel).toHaveClass('max-w-2xl');

    rerender(<Modal {...defaultProps} size="xl" />);
    panel = screen.getByRole('dialog');
    expect(panel).toHaveClass('max-w-4xl');
  });

  it('handles ESC key press', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    
    render(<Modal {...defaultProps} onClose={onClose} />);
    
    await user.keyboard('{Escape}');
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });
});