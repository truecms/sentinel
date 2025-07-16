import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from './Input';
import { Mail, Eye } from 'lucide-react';

describe('Input', () => {
  it('renders basic input', () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Input label="Email Address" id="email" />);
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
  });

  it('renders with error', () => {
    render(<Input error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('renders with help text', () => {
    render(<Input helpText="Enter your email address" />);
    expect(screen.getByText('Enter your email address')).toBeInTheDocument();
  });

  it('does not show help text when error is present', () => {
    render(<Input helpText="Help text" error="Error message" />);
    expect(screen.queryByText('Help text')).not.toBeInTheDocument();
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('renders with left icon', () => {
    render(<Input leftIcon={Mail} placeholder="Email" />);
    const input = screen.getByPlaceholderText('Email');
    expect(input).toHaveClass('pl-10');
  });

  it('renders with right element', () => {
    render(
      <Input 
        placeholder="Password" 
        rightElement={<Eye className="h-5 w-5 cursor-pointer" />} 
      />
    );
    const input = screen.getByPlaceholderText('Password');
    expect(input).toHaveClass('pr-10');
  });

  it('handles user input', async () => {
    const user = userEvent.setup();
    render(<Input placeholder="Type here" />);
    const input = screen.getByPlaceholderText('Type here');
    
    await user.type(input, 'Hello World');
    expect(input).toHaveValue('Hello World');
  });

  it('applies disabled state', () => {
    render(<Input disabled placeholder="Disabled input" />);
    const input = screen.getByPlaceholderText('Disabled input');
    expect(input).toBeDisabled();
  });

  it('forwards ref correctly', () => {
    const ref = { current: null };
    render(<Input ref={ref} placeholder="Input with ref" />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });
});