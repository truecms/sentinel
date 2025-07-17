import { useState, useEffect } from 'react'
import { sitesApi } from '../services/sitesApi'

export const useSiteCount = () => {
  const [siteCount, setSiteCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCount = async () => {
      try {
        const response = await sitesApi.getOverview({ limit: 1 })
        setSiteCount(response.pagination.total)
      } catch (error) {
        console.error('Failed to fetch site count:', error)
        setSiteCount(null)
      } finally {
        setLoading(false)
      }
    }

    fetchCount()
  }, [])

  return { siteCount, loading }
}