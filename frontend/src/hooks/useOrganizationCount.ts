import { useState, useEffect } from 'react'
import { apiClient } from '../utils/api'

export const useOrganizationCount = () => {
  const [organizationCount, setOrganizationCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCount = async () => {
      try {
        const response = await apiClient.get('/organizations/')
        setOrganizationCount(response.data.length)
      } catch (error) {
        console.error('Failed to fetch organization count:', error)
        setOrganizationCount(null)
      } finally {
        setLoading(false)
      }
    }

    fetchCount()
  }, [])

  return { organizationCount, loading }
}