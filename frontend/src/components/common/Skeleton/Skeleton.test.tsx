import React from 'react'
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { Skeleton } from './Skeleton'

describe('Skeleton', () => {
  it('renders with default props', () => {
    const { container } = render(<Skeleton />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toBeInTheDocument()
    expect(skeleton).toHaveClass('animate-pulse')
    expect(skeleton).toHaveClass('bg-neutral-200')
    expect(skeleton).toHaveClass('dark:bg-neutral-700')
    expect(skeleton).toHaveClass('rounded-md')
  })

  it('renders with custom dimensions', () => {
    const { container } = render(<Skeleton width={200} height={100} />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveStyle({ width: '200px', height: '100px' })
  })

  it('renders with string dimensions', () => {
    const { container } = render(<Skeleton width="50%" height="2rem" />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveStyle({ width: '50%', height: '2rem' })
  })

  it('renders with different variants', () => {
    const { rerender, container } = render(<Skeleton variant="rectangular" />)
    let skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('rounded-md')

    rerender(<Skeleton variant="circular" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('rounded-full')

    rerender(<Skeleton variant="text" />)
    skeleton = container.firstChild as HTMLElement
    expect(skeleton).toHaveClass('rounded')
  })

  it('disables animation when specified', () => {
    const { container } = render(<Skeleton animation="none" />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).not.toHaveClass('animate-pulse')
  })

  it('applies additional className', () => {
    const { container } = render(<Skeleton className="custom-skeleton" />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveClass('custom-skeleton')
  })

  it('renders with wave animation', () => {
    const { container } = render(<Skeleton animation="wave" />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveClass('overflow-hidden')
    expect(skeleton).toHaveClass('relative')
    expect(skeleton.querySelector('.absolute')).toBeInTheDocument()
  })

  it('combines multiple props correctly', () => {
    const { container } = render(
      <Skeleton
        width={300}
        height={50}
        variant="circular"
        animation="none"
        className="custom"
      />
    )
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveStyle({ width: '300px', height: '50px' })
    expect(skeleton).toHaveClass('rounded-full')
    expect(skeleton).not.toHaveClass('animate-pulse')
    expect(skeleton).toHaveClass('custom')
  })

  it('uses default width and height', () => {
    const { container } = render(<Skeleton />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveStyle({ width: '100%', height: '1rem' })
  })

  it('applies pulse animation by default', () => {
    const { container } = render(<Skeleton />)
    const skeleton = container.firstChild as HTMLElement
    
    expect(skeleton).toHaveClass('animate-pulse')
  })
})