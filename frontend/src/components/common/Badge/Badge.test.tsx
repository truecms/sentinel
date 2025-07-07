import React from 'react'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge } from './Badge'

describe('Badge', () => {
  it('renders with children text', () => {
    render(<Badge>New</Badge>)
    expect(screen.getByText('New')).toBeInTheDocument()
  })

  it('renders with different variants', () => {
    const { rerender, container } = render(<Badge variant="default">Default</Badge>)
    let badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('bg-neutral-100')
    expect(badge).toHaveClass('text-neutral-700')

    rerender(<Badge variant="success">Success</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('badge-success')

    rerender(<Badge variant="warning">Warning</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('badge-warning')

    rerender(<Badge variant="danger">Danger</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('badge-danger')

    rerender(<Badge variant="info">Info</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('badge-info')
  })

  it('renders with different sizes', () => {
    const { rerender, container } = render(<Badge size="sm">Small</Badge>)
    let badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('text-xs')
    expect(badge).toHaveClass('px-2')
    expect(badge).toHaveClass('py-0.5')

    rerender(<Badge size="md">Medium</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('text-sm')
    expect(badge).toHaveClass('px-2.5')
    expect(badge).toHaveClass('py-0.5')

    rerender(<Badge size="lg">Large</Badge>)
    badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('text-base')
    expect(badge).toHaveClass('px-3')
    expect(badge).toHaveClass('py-1')
  })

  it('applies additional className', () => {
    const { container } = render(<Badge className="custom-badge">Custom</Badge>)
    const badge = container.firstChild as HTMLElement
    expect(badge).toHaveClass('custom-badge')
  })

  it('renders with number content', () => {
    render(<Badge>{42}</Badge>)
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('applies correct styling for success variant', () => {
    const { container } = render(<Badge variant="success">Success</Badge>)
    const badge = container.firstChild as HTMLElement
    
    expect(badge).toHaveClass('badge-success')
  })

  it('combines multiple props correctly', () => {
    const { container } = render(
      <Badge variant="danger" size="lg" className="custom">
        Complex Badge
      </Badge>
    )
    const badge = container.firstChild as HTMLElement
    
    expect(badge).toHaveClass('badge-danger')
    expect(badge).toHaveClass('text-base')
    expect(badge).toHaveClass('px-3')
    expect(badge).toHaveClass('py-1')
    expect(badge).toHaveClass('custom')
  })
})