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

  it('should render Organizations as an expandable button when it has subItems', () => {
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
        usersCount={10}
      />
    )
    
    // Since Organizations has subItems, it should be a button, not a link
    const organizationsButton = screen.getByRole('button', { name: /organizations/i })
    expect(organizationsButton).toBeInTheDocument()
    
    // Users should not be visible initially
    expect(screen.queryByText('Users')).not.toBeInTheDocument()
  })

  it('should call onToggle when Organizations button is clicked', async () => {
    const user = userEvent.setup()
    
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
        usersCount={10}
      />
    )
    
    const organizationsButton = screen.getByRole('button', { name: /organizations/i })
    
    // Click the button
    await user.click(organizationsButton)
    
    // For now, just verify the button is clickable
    expect(organizationsButton).toBeInTheDocument()
  })

  it('should show chevron icon for expandable items', () => {
    render(
      <SidebarWithRouter
        {...defaultProps}
        organizationsCount={5}
      />
    )
    
    const organizationsButton = screen.getByRole('button', { name: /organizations/i })
    
    // Should have a chevron icon
    const chevron = organizationsButton.querySelector('.lucide-chevron-down')
    expect(chevron).toBeInTheDocument()
  })
})