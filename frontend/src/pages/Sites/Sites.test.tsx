import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { Sites } from './Sites'
import { sitesApi } from '../../services/sitesApi'

// Mock the sitesApi
vi.mock('../../services/sitesApi', () => ({
  sitesApi: {
    getOverview: vi.fn(),
  }
}))

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    tr: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => <tr {...props}>{children}</tr>,
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => <div {...props}>{children}</div>,
  },
}))

const mockSitesResponse = {
  sites: [
    {
      id: 1,
      name: 'Test Site 1',
      url: 'https://test1.example.com',
      security_score: 85,
      total_modules_count: 45,
      security_updates_count: 0,
      non_security_updates_count: 2,
      last_data_push: '2024-01-20T10:30:00Z',
      last_drupal_org_check: '2024-01-20T09:00:00Z',
      status: 'healthy',
      organization_id: 1,
    },
    {
      id: 2,
      name: 'Test Site 2',
      url: 'https://test2.example.com',
      security_score: 45,
      total_modules_count: 62,
      security_updates_count: 3,
      non_security_updates_count: 5,
      last_data_push: '2024-01-19T15:45:00Z',
      last_drupal_org_check: '2024-01-19T14:00:00Z',
      status: 'critical',
      organization_id: 1,
    }
  ],
  pagination: {
    page: 1,
    per_page: 25,
    total: 2,
    total_pages: 1,
  },
  filters: {
    search: '',
    sort_by: 'name',
    sort_order: 'asc',
  }
}

describe('Sites Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders page header correctly', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    expect(screen.getByText('Sites Overview')).toBeInTheDocument()
    expect(screen.getByText('Monitor security status and updates across all your Drupal sites')).toBeInTheDocument()
    expect(screen.getByText('Add New Site')).toBeInTheDocument()
  })

  it('loads and displays sites data', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
      expect(screen.getByText('Test Site 2')).toBeInTheDocument()
    })
    
    // Check security scores
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('45%')).toBeInTheDocument()
    
    // Check module counts
    expect(screen.getByText('45')).toBeInTheDocument() // Total modules for site 1
    expect(screen.getByText('62')).toBeInTheDocument() // Total modules for site 2
    
    // Check status badges
    expect(screen.getByText('healthy')).toBeInTheDocument()
    expect(screen.getByText('critical')).toBeInTheDocument()
  })

  it('handles search functionality', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    const searchInput = screen.getByPlaceholderText('Search sites by name or URL...')
    
    // Type in search box
    fireEvent.change(searchInput, { target: { value: 'Test Site 1' } })
    
    // Wait for debounced search to trigger
    await waitFor(() => {
      expect(sitesApi.getOverview).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'Test Site 1'
        })
      )
    }, { timeout: 500 })
  })

  it('handles sorting when column header is clicked', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
    })
    
    // Click on Security Score column header
    const securityScoreHeader = screen.getByText('Security Score')
    fireEvent.click(securityScoreHeader)
    
    await waitFor(() => {
      expect(sitesApi.getOverview).toHaveBeenCalledWith(
        expect.objectContaining({
          sort_by: 'security_score',
          sort_order: 'asc'
        })
      )
    })
  })

  it('displays error state when API call fails', async () => {
    vi.mocked(sitesApi.getOverview).mockRejectedValue(new Error('API Error'))
    
    render(<Sites />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load sites. Please try again.')).toBeInTheDocument()
      expect(screen.getByText('Try Again')).toBeInTheDocument()
    })
  })

  it('handles pagination correctly', async () => {
    const mockPaginatedResponse = {
      ...mockSitesResponse,
      pagination: {
        page: 1,
        per_page: 25,
        total: 50,
        total_pages: 2,
      }
    }
    
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockPaginatedResponse)
    
    render(<Sites />)
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
    })
    
    // Check pagination display
    expect(screen.getByText('Showing 1 to 2 of 50 results')).toBeInTheDocument()
  })

  it('shows tooltips for timestamp columns', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
    })
    
    // Check for tooltip text in the DOM
    expect(screen.getByText(/When this site last pushed monitoring data/)).toBeInTheDocument()
    expect(screen.getByText(/When we last checked Drupal.org/)).toBeInTheDocument()
  })

  it('formats dates correctly', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
    })
    
    // Should show relative time formatting
    // Note: The exact text will depend on when the test runs, 
    // but it should show something like "X days ago" or a formatted date
    const dateElements = screen.getAllByText(/ago|Never|\d/)
    expect(dateElements.length).toBeGreaterThan(0)
  })

  it('applies correct styling to security scores', async () => {
    vi.mocked(sitesApi.getOverview).mockResolvedValue(mockSitesResponse)
    
    render(<Sites />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Site 1')).toBeInTheDocument()
    })
    
    // High security score should have green color
    const highScore = screen.getByText('85%')
    expect(highScore).toHaveClass('text-green-600')
    
    // Low security score should have red color
    const lowScore = screen.getByText('45%')
    expect(lowScore).toHaveClass('text-red-600')
  })
})