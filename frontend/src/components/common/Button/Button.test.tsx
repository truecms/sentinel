import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'
import { ArrowRight } from 'lucide-react'

describe('Button', () => {
  it('renders with children text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-primary-600')

    rerender(<Button variant="secondary">Secondary</Button>)
    expect(button).toHaveClass('bg-white')

    rerender(<Button variant="outline">Outline</Button>)
    expect(button).toHaveClass('border-neutral-300')

    rerender(<Button variant="ghost">Ghost</Button>)
    expect(button).toHaveClass('hover:bg-neutral-100')

    rerender(<Button variant="danger">Danger</Button>)
    expect(button).toHaveClass('bg-danger-600')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="small">Small</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('px-3 py-1.5 text-sm')

    rerender(<Button size="medium">Medium</Button>)
    expect(button).toHaveClass('px-4 py-2 text-sm')

    rerender(<Button size="large">Large</Button>)
    expect(button).toHaveClass('px-6 py-3 text-base')
  })

  it('renders with icon', () => {
    render(
      <Button icon={ArrowRight} iconPosition="left">
        With Icon
      </Button>
    )
    const button = screen.getByRole('button')
    expect(button.querySelector('svg')).toBeInTheDocument()
  })

  it('renders as full width', () => {
    render(<Button fullWidth>Full Width</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('w-full')
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<Button onClick={handleClick}>Click me</Button>)
    const button = screen.getByRole('button')
    
    await user.click(button)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('can be disabled', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(
      <Button disabled onClick={handleClick}>
        Disabled
      </Button>
    )
    const button = screen.getByRole('button')
    
    expect(button).toBeDisabled()
    expect(button).toHaveClass('opacity-50 cursor-not-allowed')
    
    await user.click(button)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    const button = screen.getByRole('button')
    
    expect(button).toBeDisabled()
    expect(button).toHaveClass('relative')
    expect(button.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('renders as different HTML element when "as" prop is provided', () => {
    render(
      <Button as="a" href="/test">
        Link Button
      </Button>
    )
    
    const link = screen.getByRole('link', { name: 'Link Button' })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/test')
  })

  it('applies additional className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('forwards ref', () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<Button ref={ref}>With Ref</Button>)
    
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    expect(ref.current?.textContent).toBe('With Ref')
  })
})