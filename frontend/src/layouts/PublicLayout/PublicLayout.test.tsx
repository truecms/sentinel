import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { PublicLayout } from './PublicLayout'

// Mock the components that will be created
vi.mock('../../components/public/PublicHeader/PublicHeader', () => ({
  PublicHeader: () => <header data-testid="public-header">Public Header</header>
}))

vi.mock('../../components/public/PublicFooter/PublicFooter', () => ({
  PublicFooter: () => <footer data-testid="public-footer">Public Footer</footer>
}))

describe('PublicLayout', () => {
  const renderWithRouter = (children: React.ReactNode) => {
    return render(
      <MemoryRouter>
        <PublicLayout>{children}</PublicLayout>
      </MemoryRouter>
    )
  }

  it('renders children content', () => {
    renderWithRouter(<div data-testid="test-content">Test Content</div>)
    
    expect(screen.getByTestId('test-content')).toBeInTheDocument()
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders public header', () => {
    renderWithRouter(<div>Content</div>)
    
    expect(screen.getByTestId('public-header')).toBeInTheDocument()
  })

  it('renders public footer', () => {
    renderWithRouter(<div>Content</div>)
    
    expect(screen.getByTestId('public-footer')).toBeInTheDocument()
  })

  it('has correct layout structure', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const layout = container.firstChild
    expect(layout).toHaveClass('min-h-screen', 'flex', 'flex-col')
  })

  it('main content area has flex-grow', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const main = container.querySelector('main')
    expect(main).toBeInTheDocument()
    expect(main).toHaveClass('flex-grow')
  })

  it('applies responsive padding to main content', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const main = container.querySelector('main')
    expect(main).toHaveClass('px-4', 'sm:px-6', 'lg:px-8')
  })

  it('renders multiple children correctly', () => {
    renderWithRouter(
      <>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
        <div data-testid="child-3">Child 3</div>
      </>
    )
    
    expect(screen.getByTestId('child-1')).toBeInTheDocument()
    expect(screen.getByTestId('child-2')).toBeInTheDocument()
    expect(screen.getByTestId('child-3')).toBeInTheDocument()
  })

  it('maintains correct DOM hierarchy', () => {
    const { container } = renderWithRouter(<div data-testid="content">Content</div>)
    
    const header = container.querySelector('header')
    const main = container.querySelector('main')
    const footer = container.querySelector('footer')
    const content = screen.getByTestId('content')
    
    // Verify order
    expect(header?.nextElementSibling).toBe(main)
    expect(main?.nextElementSibling).toBe(footer)
    
    // Verify content is inside main
    expect(main?.contains(content)).toBe(true)
  })

  it('supports theme classes', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const layout = container.firstChild
    expect(layout).toHaveClass('bg-white', 'dark:bg-neutral-900')
  })

  it('sets correct accessibility attributes', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const main = container.querySelector('main')
    expect(main).toHaveAttribute('role', 'main')
  })

  it('handles empty children gracefully', () => {
    const { container } = renderWithRouter(null)
    
    expect(container.querySelector('header')).toBeInTheDocument()
    expect(container.querySelector('main')).toBeInTheDocument()
    expect(container.querySelector('footer')).toBeInTheDocument()
  })

  it('supports className prop', () => {
    const TestComponent = () => (
      <PublicLayout className="custom-class">
        <div>Content</div>
      </PublicLayout>
    )
    
    const { container } = render(
      <MemoryRouter>
        <TestComponent />
      </MemoryRouter>
    )
    
    const layout = container.firstChild
    expect(layout).toHaveClass('custom-class')
  })

  it('renders with skip navigation link', () => {
    renderWithRouter(<div>Content</div>)
    
    const skipLink = screen.getByText('Skip to main content')
    expect(skipLink).toBeInTheDocument()
    expect(skipLink).toHaveClass('sr-only', 'focus:not-sr-only')
    expect(skipLink).toHaveAttribute('href', '#main-content')
  })

  it('main content has correct id for skip link', () => {
    const { container } = renderWithRouter(<div>Content</div>)
    
    const main = container.querySelector('main')
    expect(main).toHaveAttribute('id', 'main-content')
  })
})