import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Card, CardHeader, CardContent, CardFooter } from './Card'

describe('Card', () => {
  it('renders with children', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('applies default styles', () => {
    const { container } = render(<Card>Content</Card>)
    const card = container.firstChild as HTMLElement
    
    expect(card).toHaveClass('bg-white')
    expect(card).toHaveClass('dark:bg-neutral-800')
    expect(card).toHaveClass('rounded-lg')
    expect(card).toHaveClass('border')
  })

  it('renders with different variants', () => {
    const { rerender, container } = render(<Card variant="default">Default</Card>)
    let card = container.firstChild as HTMLElement
    expect(card).toHaveClass('border-neutral-200')

    rerender(<Card variant="bordered">Bordered</Card>)
    card = container.firstChild as HTMLElement
    expect(card).toHaveClass('border-2')

    rerender(<Card variant="elevated">Elevated</Card>)
    card = container.firstChild as HTMLElement
    expect(card).toHaveClass('shadow-lg')

    rerender(<Card variant="flat">Flat</Card>)
    card = container.firstChild as HTMLElement
    expect(card).toHaveClass('border-transparent')
  })

  it('applies padding when specified', () => {
    const { container } = render(<Card padding>Padded content</Card>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('p-6')
  })

  it('handles click events when interactive', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    const { container } = render(
      <Card interactive onClick={handleClick}>
        Interactive card
      </Card>
    )
    const card = container.firstChild as HTMLElement
    
    expect(card).toHaveClass('cursor-pointer')
    expect(card).toHaveClass('transition-all')
    
    await user.click(card)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies additional className', () => {
    const { container } = render(<Card className="custom-class">Custom</Card>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('custom-class')
  })
})

describe('CardHeader', () => {
  it('renders with children', () => {
    render(
      <CardHeader>
        <h2>Card Title</h2>
      </CardHeader>
    )
    expect(screen.getByText('Card Title')).toBeInTheDocument()
  })

  it('applies default styles', () => {
    const { container } = render(<CardHeader>Header</CardHeader>)
    const header = container.firstChild as HTMLElement
    
    expect(header).toHaveClass('px-6')
    expect(header).toHaveClass('py-4')
    expect(header).toHaveClass('border-b')
  })

  it('applies additional className', () => {
    const { container } = render(
      <CardHeader className="custom-header">Header</CardHeader>
    )
    const header = container.firstChild as HTMLElement
    expect(header).toHaveClass('custom-header')
  })
})

describe('CardContent', () => {
  it('renders with children', () => {
    render(
      <CardContent>
        <p>Card body content</p>
      </CardContent>
    )
    expect(screen.getByText('Card body content')).toBeInTheDocument()
  })

  it('applies default styles', () => {
    const { container } = render(<CardContent>Content</CardContent>)
    const content = container.firstChild as HTMLElement
    
    expect(content).toHaveClass('px-6')
    expect(content).toHaveClass('py-4')
  })

  it('applies additional className', () => {
    const { container } = render(
      <CardContent className="custom-content">Content</CardContent>
    )
    const content = container.firstChild as HTMLElement
    expect(content).toHaveClass('custom-content')
  })
})

describe('CardFooter', () => {
  it('renders with children', () => {
    render(
      <CardFooter>
        <button>Action</button>
      </CardFooter>
    )
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  it('applies default styles', () => {
    const { container } = render(<CardFooter>Footer</CardFooter>)
    const footer = container.firstChild as HTMLElement
    
    expect(footer).toHaveClass('px-6')
    expect(footer).toHaveClass('py-4')
    expect(footer).toHaveClass('border-t')
    expect(footer).toHaveClass('bg-neutral-50')
  })

  it('applies additional className', () => {
    const { container } = render(
      <CardFooter className="custom-footer">Footer</CardFooter>
    )
    const footer = container.firstChild as HTMLElement
    expect(footer).toHaveClass('custom-footer')
  })
})

describe('Card composition', () => {
  it('renders complete card with all sections', () => {
    render(
      <Card>
        <CardHeader>
          <h2>Title</h2>
        </CardHeader>
        <CardContent>
          <p>Body content</p>
        </CardContent>
        <CardFooter>
          <button>Action</button>
        </CardFooter>
      </Card>
    )
    
    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Body content')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })
})