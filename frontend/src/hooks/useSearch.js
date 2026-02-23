import { useState, useCallback } from 'react'
import api from '../services/api'

const DEFAULT_SOURCES = ['duckduckgo', 'arxiv']

export default function useSearch() {
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [sourcesStatus, setSourcesStatus] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState({
    sources: DEFAULT_SOURCES,
    category: 'all',
    language: 'all',
    time_range: null,
  })

  const search = useCallback(async (searchQuery) => {
    const q = (searchQuery || '').trim()
    if (!q) return

    setQuery(q)
    setLoading(true)
    setError(null)

    try {
      const data = await api.post('/search', {
        query: q,
        sources: filters.sources,
        filters: {
          time_range: filters.time_range || null,
        },
      })
      let items = data.results || []

      // Client-side category filter
      if (filters.category && filters.category !== 'all') {
        items = items.filter((item) => item.category === filters.category)
      }

      setResults(items)
      setTotal(data.total || 0)
      setSourcesStatus(data.sources_status || {})
    } catch (err) {
      setError(err.message || 'Search failed')
      setResults([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [filters])

  const updateSources = useCallback((sources) => {
    setFilters((prev) => ({ ...prev, sources }))
  }, [])

  const updateCategory = useCallback((category) => {
    setFilters((prev) => ({ ...prev, category }))
  }, [])

  const updateTimeRange = useCallback((timeRange) => {
    setFilters((prev) => ({ ...prev, time_range: timeRange }))
  }, [])

  return {
    results,
    total,
    sourcesStatus,
    loading,
    error,
    query,
    filters,
    search,
    setFilters,
    updateSources,
    updateCategory,
    updateTimeRange,
  }
}
