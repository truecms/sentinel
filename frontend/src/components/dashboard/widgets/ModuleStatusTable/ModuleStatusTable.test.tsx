import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ModuleStatusTable } from './ModuleStatusTable'
import type { ModuleStatus } from '../../../../types/dashboard'

describe('ModuleStatusTable', () => {
  const mockModules: ModuleStatus[] = [
    {
      id: '1',
      name: 'views',
      currentVersion: '8.9.1',
      latestVersion: '8.9.5',
      securityUpdate: true,
      lastUpdated: new Date('2024-01-15'),
      sites: 5,
    },
    {
      id: '2',
      name: 'pathauto',
      currentVersion: '1.11.0',
      latestVersion: '1.11.0',
      securityUpdate: false,
      lastUpdated: new Date('2024-01-10'),
      sites: 3,
    },
    {
      id: '3',
      name: 'metatag',
      currentVersion: '1.22.0',
      latestVersion: '1.23.0',
      securityUpdate: false,
      lastUpdated: new Date('2024-01-05'),
      sites: 4,
    },
  ]

  it('renders module data correctly', () => {
    render(<ModuleStatusTable modules={mockModules} />)
    
    expect(screen.getByText('views')).toBeInTheDocument()
    expect(screen.getByText('8.9.1')).toBeInTheDocument()
    expect(screen.getByText('8.9.5')).toBeInTheDocument()
    expect(screen.getByText('Security Update')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<ModuleStatusTable modules={[]} loading={true} />)
    
    const skeletons = screen.getAllByTestId((content, element) => {
      return element?.classList.contains('animate-pulse') || false
    })
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('shows error state', () => {
    const error = new Error('Failed to load modules')
    render(<ModuleStatusTable modules={[]} error={error} />)
    
    expect(screen.getByText('Error loading modules')).toBeInTheDocument()
    expect(screen.getByText('Failed to load modules')).toBeInTheDocument()
  })

  it('shows empty state', () => {
    render(<ModuleStatusTable modules={[]} />)
    
    expect(screen.getByText('No modules found')).toBeInTheDocument()
  })

  it('handles row click events', () => {
    const handleRowClick = vi.fn()
    render(
      <ModuleStatusTable
        modules={mockModules}
        onRowClick={handleRowClick}
      />
    )
    
    fireEvent.click(screen.getByText('views'))
    expect(handleRowClick).toHaveBeenCalledWith(mockModules[0])
  })

  it('filters modules by search term', async () => {
    const handleFilterChange = vi.fn()
    render(
      <ModuleStatusTable
        modules={mockModules}
        filters={{
          searchTerm: '',
          securityOnly: false,
          onFilterChange: handleFilterChange,
        }}
      />
    )
    
    const searchInput = screen.getByPlaceholderText('Search modules...')
    fireEvent.change(searchInput, { target: { value: 'meta' } })
    
    await waitFor(() => {
      expect(handleFilterChange).toHaveBeenCalledWith({ searchTerm: 'meta' })
    })
  })

  it('filters security updates only', () => {
    const handleFilterChange = vi.fn()
    render(
      <ModuleStatusTable
        modules={mockModules}
        filters={{
          searchTerm: '',
          securityOnly: false,
          onFilterChange: handleFilterChange,
        }}
      />
    )
    
    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)
    
    expect(handleFilterChange).toHaveBeenCalledWith({ securityOnly: true })
  })

  it('sorts modules correctly', () => {
    const handleSort = vi.fn()
    render(
      <ModuleStatusTable
        modules={mockModules}
        sorting={{
          field: 'name',
          direction: 'asc',
          onSort: handleSort,
        }}
      />
    )
    
    const nameHeader = screen.getByText('Module Name')
    fireEvent.click(nameHeader)
    
    expect(handleSort).toHaveBeenCalledWith('name')
  })

  it('handles pagination correctly', () => {
    const handlePageChange = vi.fn()
    const manyModules = Array.from({ length: 15 }, (_, i) => ({
      id: String(i),
      name: `module-${i}`,
      currentVersion: '1.0.0',
      lastUpdated: new Date(),
      sites: 1,
      securityUpdate: false,
    }))
    
    render(
      <ModuleStatusTable
        modules={manyModules}
        pagination={{
          page: 1,
          pageSize: 10,
          total: 15,
          onPageChange: handlePageChange,
        }}
      />
    )
    
    expect(screen.getByText('Showing 1 to 10 of 15 results')).toBeInTheDocument()
    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()
    
    // Click next page
    const nextButton = screen.getAllByRole('button').find(btn => 
      btn.querySelector('svg')?.classList.contains('lucide-chevron-right')
    )
    fireEvent.click(nextButton!)
    
    expect(handlePageChange).toHaveBeenCalledWith(2)
  })

  it('disables pagination buttons appropriately', () => {
    render(
      <ModuleStatusTable
        modules={mockModules}
        pagination={{
          page: 1,
          pageSize: 10,
          total: 3,
          onPageChange: vi.fn(),
        }}
      />
    )
    
    const [prevButton, nextButton] = screen.getAllByRole('button').filter(btn =>
      btn.querySelector('svg')
    )
    
    expect(prevButton).toBeDisabled()
    expect(nextButton).toBeDisabled()
  })

  it('displays correct status badges', () => {
    render(<ModuleStatusTable modules={mockModules} />)
    
    expect(screen.getByText('Security Update')).toBeInTheDocument()
    expect(screen.getByText('Update Available')).toBeInTheDocument()
    expect(screen.getByText('Up to Date')).toBeInTheDocument()
  })

  it('formats dates correctly', () => {
    render(<ModuleStatusTable modules={mockModules} />)
    
    expect(screen.getByText('Jan 15, 2024')).toBeInTheDocument()
    expect(screen.getByText('Jan 10, 2024')).toBeInTheDocument()
    expect(screen.getByText('Jan 5, 2024')).toBeInTheDocument()
  })
})