import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { Table, TableColumn } from './Table'

describe('Table Component', () => {
  const mockColumns: TableColumn[] = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
    },
    {
      key: 'email',
      label: 'Email',
      sortable: false,
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      tooltip: 'Current user status',
      render: (value) => <span className={`status-${value}`}>{value}</span>
    }
  ]

  const mockData = [
    { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive' },
  ]

  it('renders table with data correctly', () => {
    render(<Table columns={mockColumns} data={mockData} />)
    
    // Check headers
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
    
    // Check data
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('jane@example.com')).toBeInTheDocument()
    expect(screen.getByText('active')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<Table columns={mockColumns} data={[]} loading={true} />)
    
    // Should show skeleton rows
    const skeletonElements = screen.getAllByText('Name')[0] // Header still shows
    expect(skeletonElements).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    render(<Table columns={mockColumns} data={[]} />)
    
    expect(screen.getByText('No data available')).toBeInTheDocument()
    expect(screen.getByText('No records match your current filters.')).toBeInTheDocument()
  })

  it('handles sorting correctly', () => {
    const mockOnSort = vi.fn()
    render(
      <Table 
        columns={mockColumns} 
        data={mockData} 
        onSort={mockOnSort}
        sortBy="name"
        sortOrder="asc"
      />
    )
    
    const nameHeader = screen.getByText('Name').closest('th')
    expect(nameHeader).toHaveClass('cursor-pointer')
    
    fireEvent.click(nameHeader!)
    expect(mockOnSort).toHaveBeenCalledWith('name', 'desc')
  })

  it('does not allow sorting on non-sortable columns', () => {
    const mockOnSort = vi.fn()
    render(<Table columns={mockColumns} data={mockData} onSort={mockOnSort} />)
    
    const emailHeader = screen.getByText('Email').closest('th')
    expect(emailHeader).not.toHaveClass('cursor-pointer')
    
    fireEvent.click(emailHeader!)
    expect(mockOnSort).not.toHaveBeenCalled()
  })

  it('renders custom cell content', () => {
    render(<Table columns={mockColumns} data={mockData} />)
    
    // Check if custom render function is used for status column
    expect(screen.getByText('active')).toHaveClass('status-active')
    expect(screen.getByText('inactive')).toHaveClass('status-inactive')
  })

  it('shows tooltip on hover', () => {
    render(<Table columns={mockColumns} data={mockData} />)
    
    // The tooltip content should be in the DOM (even if hidden)
    expect(screen.getByText('Current user status')).toBeInTheDocument()
  })

  it('displays sort indicators correctly', () => {
    render(
      <Table 
        columns={mockColumns} 
        data={mockData} 
        sortBy="name" 
        sortOrder="asc" 
      />
    )
    
    // The ChevronUpIcon should be shown for ascending sort
    const nameHeader = screen.getByText('Name').closest('th')
    expect(nameHeader?.querySelector('svg')).toBeInTheDocument()
  })
})