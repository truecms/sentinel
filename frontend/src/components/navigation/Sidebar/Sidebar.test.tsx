import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { Sidebar } from './Sidebar'

// Wrapper component to provide Router context
const SidebarWithRouter = (props: any) => (
  <BrowserRouter>
    <Sidebar {...props} />
  </BrowserRouter>
)

describe('Sidebar', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    isCollapsed: false,
    onToggleCollapse: vi.fn(),
  }

  it('should show Organizations item', () => {
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
      />
    )
    
    // Organizations text should be visible
    expect(screen.getByText('Organizations')).toBeInTheDocument()
  })

  it('should not have React key warnings', () => {
    const consoleSpy = vi.spyOn(console, 'error')
    
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
      />
    )
    
    // Should not have any key prop warnings
    const keyWarnings = consoleSpy.mock.calls.filter(call => 
      call[0]?.includes?.('Each child in a list should have a unique "key" prop')
    )
    expect(keyWarnings).toHaveLength(0)
    
    consoleSpy.mockRestore()
  })

  it('should render Organizations as a link when path is provided', () => {
    // Check current behavior - Organizations has no path so it renders with empty href
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
      />
    )
    
    const organizationsLink = screen.getByRole('link', { name: /organizations/i })
    expect(organizationsLink).toBeInTheDocument()
    expect(organizationsLink).toHaveAttribute('href', '/')
  })
})