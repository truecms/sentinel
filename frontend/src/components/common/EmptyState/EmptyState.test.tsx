import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EmptyState } from './EmptyState'
import { FileText } from 'lucide-react'

describe('EmptyState', () => {
  it('renders with title and description', () => {
    render(
      <EmptyState
        title="No data found"
        description="Start by adding some data to see it here"
      />
    )
    
    expect(screen.getByText('No data found')).toBeInTheDocument()
    expect(screen.getByText('Start by adding some data to see it here')).toBeInTheDocument()
  })

  it('renders with default icon', () => {
    const { container } = render(
      <EmptyState
        title="No documents"
        description="Upload your first document"
      />
    )
    
    const icon = container.querySelector('svg')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveClass('w-12')
    expect(icon).toHaveClass('h-12')
  })

  it('renders with string icon types', () => {
    const { rerender, container } = render(
      <EmptyState icon="search" title="No results" />
    )
    expect(container.querySelector('svg')).toBeInTheDocument()

    rerender(<EmptyState icon="security" title="No security issues" />)
    expect(container.querySelector('svg')).toBeInTheDocument()

    rerender(<EmptyState icon="error" title="An error occurred" />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('renders with custom icon element', () => {
    const { container } = render(
      <EmptyState
        icon={<FileText className="w-16 h-16 text-primary-500" />}
        title="No documents"
      />
    )
    
    const icon = container.querySelector('svg')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveClass('w-16')
    expect(icon).toHaveClass('h-16')
    expect(icon).toHaveClass('text-primary-500')
  })

  it('renders action button', () => {
    render(
      <EmptyState
        title="No items"
        action={{
          label: 'Add item',
          onClick: () => {},
        }}
      />
    )
    
    expect(screen.getByRole('button', { name: 'Add item' })).toBeInTheDocument()
  })

  it('handles action button click', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(
      <EmptyState
        title="No items"
        action={{
          label: 'Add item',
          onClick: handleClick,
        }}
      />
    )
    
    const button = screen.getByRole('button', { name: 'Add item' })
    await user.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies additional className', () => {
    const { container } = render(
      <EmptyState title="No data" className="custom-class" />
    )
    
    const emptyState = container.firstChild as HTMLElement
    expect(emptyState).toHaveClass('custom-class')
  })

  it('renders without description', () => {
    render(<EmptyState title="No data available" />)
    
    expect(screen.getByText('No data available')).toBeInTheDocument()
    expect(screen.queryByText('description')).not.toBeInTheDocument()
  })

  it('renders with all props combined', () => {
    const handleClick = vi.fn()
    
    render(
      <EmptyState
        icon="search"
        title="No documents found"
        description="Upload your first document to get started"
        action={{
          label: 'Upload Document',
          onClick: handleClick,
        }}
        className="custom-empty-state"
      />
    )
    
    expect(screen.getByText('No documents found')).toBeInTheDocument()
    expect(screen.getByText('Upload your first document to get started')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Upload Document' })).toBeInTheDocument()
  })

  it('applies correct styling classes', () => {
    render(
      <EmptyState 
        title="Empty state title"
        description="Empty state description"
      />
    )
    
    const title = screen.getByText('Empty state title')
    expect(title).toHaveClass('text-lg')
    expect(title).toHaveClass('font-semibold')
    expect(title).toHaveClass('text-neutral-900')
    expect(title).toHaveClass('dark:text-neutral-100')
    
    const description = screen.getByText('Empty state description')
    expect(description).toHaveClass('text-sm')
    expect(description).toHaveClass('text-neutral-600')
    expect(description).toHaveClass('dark:text-neutral-400')
  })
})