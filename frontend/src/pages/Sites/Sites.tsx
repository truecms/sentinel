import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { Globe, Search, Plus, ExternalLinkIcon } from 'lucide-react'
import { Button, Input, Badge, Table, Pagination } from '../../components/common'
import { sitesApi, type SiteOverview, type SitesOverviewParams } from '../../services/sitesApi'
import { type TableColumn } from '../../components/common/Table'

// Utility functions
const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Never'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
  
  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return date.toLocaleDateString()
}

const getStatusBadgeVariant = (status: string) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'warning': return 'warning'
    case 'critical': return 'danger'
    default: return 'neutral'
  }
}

const getSecurityScoreColor = (score: number) => {
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
  if (score >= 40) return 'text-orange-600 dark:text-orange-400'
  return 'text-red-600 dark:text-red-400'
}

export const Sites: React.FC = () => {
  const [sites, setSites] = useState<SiteOverview[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters and pagination state
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(25)
  const [totalItems, setTotalItems] = useState(0)
  const [totalPages, setTotalPages] = useState(0)

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState(search)
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300)
    return () => clearTimeout(timer)
  }, [search])

  // Load sites data
  const loadSites = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params: SitesOverviewParams = {
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage,
        search: debouncedSearch || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      }
      
      const response = await sitesApi.getOverview(params)
      setSites(response.sites)
      setTotalItems(response.pagination.total)
      setTotalPages(response.pagination.total_pages)
    } catch (err) {
      setError('Failed to load sites. Please try again.')
      console.error('Failed to load sites:', err)
    } finally {
      setLoading(false)
    }
  }, [currentPage, itemsPerPage, debouncedSearch, sortBy, sortOrder])

  // Load data on dependency changes
  useEffect(() => {
    loadSites()
  }, [debouncedSearch, sortBy, sortOrder, currentPage, itemsPerPage, loadSites])

  // Reset to first page when search or sort changes
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1)
    }
  }, [debouncedSearch, sortBy, sortOrder, currentPage])

  // Table columns configuration
  const columns: TableColumn[] = useMemo(() => [
    {
      key: 'name',
      label: 'Site Name',
      sortable: true,
      render: (value: string, row: SiteOverview) => (
        <div className="flex items-center space-x-3">
          <div>
            <div className="font-medium text-gray-900 dark:text-gray-100">{value}</div>
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <Globe className="w-3 h-3 mr-1" />
              <a 
                href={row.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-primary-600 dark:hover:text-primary-400 truncate max-w-xs"
              >
                {row.url}
              </a>
              <ExternalLinkIcon className="w-3 h-3 ml-1" />
            </div>
          </div>
        </div>
      )
    },
    {
      key: 'security_score',
      label: 'Security Score',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center">
          <span className={`text-lg font-semibold ${getSecurityScoreColor(value)}`}>
            {value}%
          </span>
        </div>
      )
    },
    {
      key: 'total_modules_count',
      label: 'Total Modules',
      sortable: true,
      render: (value: number) => (
        <span className="text-gray-900 dark:text-gray-100 font-medium">{value}</span>
      )
    },
    {
      key: 'security_updates_count',
      label: 'Security Updates',
      sortable: true,
      render: (value: number) => (
        <span className={`font-medium ${
          value > 0 
            ? 'text-red-600 dark:text-red-400' 
            : 'text-green-600 dark:text-green-400'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'non_security_updates_count',
      label: 'Other Updates',
      sortable: true,
      render: (value: number) => (
        <span className={`font-medium ${
          value > 0 
            ? 'text-yellow-600 dark:text-yellow-400' 
            : 'text-green-600 dark:text-green-400'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'last_data_push',
      label: 'Last Updated',
      sortable: true,
      tooltip: 'When this site last pushed monitoring data to our system. This indicates how current our information is.',
      render: (value: string | null) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {formatDate(value)}
        </span>
      )
    },
    {
      key: 'last_drupal_org_check',
      label: 'Last Checked',
      sortable: true,
      tooltip: 'When we last checked Drupal.org for available updates for this site\'s modules. This shows how recent our update detection is.',
      render: (value: string | null) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {formatDate(value)}
        </span>
      )
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value: string) => (
        <Badge variant={getStatusBadgeVariant(value)}>
          {value}
        </Badge>
      )
    }
  ], [])

  // Event handlers
  const handleSort = (column: string, order: 'asc' | 'desc') => {
    setSortBy(column)
    setSortOrder(order)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleItemsPerPageChange = (items: number) => {
    setItemsPerPage(items)
    setCurrentPage(1) // Reset to first page
  }

  const handleSearchChange = (value: string) => {
    setSearch(value)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Sites Overview
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Monitor security status and updates across all your Drupal sites
          </p>
        </div>
        <Button variant="primary" size="md">
          <Plus className="w-4 h-4 mr-2" />
          Add New Site
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search sites by name or URL..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-2"
            onClick={loadSites}
          >
            Try Again
          </Button>
        </div>
      )}

      {/* Sites Table */}
      <Table
        columns={columns}
        data={sites}
        loading={loading}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
      />

      {/* Pagination */}
      {!loading && sites.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={handlePageChange}
          onItemsPerPageChange={handleItemsPerPageChange}
        />
      )}
    </div>
  )
}