import { useState, useCallback } from 'react'
import api from '../services/api'

const DEFAULT_SOURCES = ['scholar', 'arxiv']

export default function useSearch() {
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [sourcesStatus, setSourcesStatus] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [queries, setQueries] = useState([])
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [filters, setFilters] = useState({
    sources: DEFAULT_SOURCES,
    category: 'all',
    language: 'all',
    time_range: null,
    semantic_filter: true,
    relevance_threshold: 40,
  })

  const search = useCallback(async (searchQueries) => {
    // Accept both string (single keyword) and array (multiple keywords)
    const queryList = Array.isArray(searchQueries) ? searchQueries : [searchQueries]
    const validQueries = queryList.map(q => (q || '').trim()).filter(q => q.length > 0)
    if (validQueries.length === 0) return

    setQueries(validQueries)
    setLoading(true)
    setError(null)
    setSelectedIds(new Set())

    try {
      const data = await api.post('/search', {
        queries: validQueries,
        sources: filters.sources,
        filters: {
          time_range: filters.time_range || null,
          semantic_filter: filters.semantic_filter,
          relevance_threshold: filters.relevance_threshold,
        },
      })
      let items = data.results || []

      // Client-side category filter
      if (filters.category && filters.category !== 'all') {
        items = items.filter((item) => item.category === filters.category)
      }

      // Add unique ID to each result for selection tracking
      items = items.map((item, index) => ({
        ...item,
        _id: item.url || `result-${index}`,
      }))

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

  const toggleSelect = useCallback((id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const selectAll = useCallback(() => {
    setSelectedIds(new Set(results.map((item) => item._id)))
  }, [results])

  const deselectAll = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  const invertSelection = useCallback(() => {
    setSelectedIds((prev) => {
      const allIds = new Set(results.map((item) => item._id))
      const next = new Set()
      allIds.forEach((id) => {
        if (!prev.has(id)) {
          next.add(id)
        }
      })
      return next
    })
  }, [results])

  const removeSelected = useCallback(() => {
    setResults((prev) => prev.filter((item) => !selectedIds.has(item._id)))
    setSelectedIds(new Set())
  }, [selectedIds])

  const getSelectedResults = useCallback(() => {
    return results.filter((item) => selectedIds.has(item._id))
  }, [results, selectedIds])

  const updateSources = useCallback((sources) => {
    setFilters((prev) => ({ ...prev, sources }))
  }, [])

  const updateCategory = useCallback((category) => {
    setFilters((prev) => ({ ...prev, category }))
  }, [])

  const updateTimeRange = useCallback((timeRange) => {
    setFilters((prev) => ({ ...prev, time_range: timeRange }))
  }, [])

  const updateSemanticFilter = useCallback((enabled) => {
    setFilters((prev) => ({ ...prev, semantic_filter: enabled }))
  }, [])

  const updateRelevanceThreshold = useCallback((threshold) => {
    setFilters((prev) => ({ ...prev, relevance_threshold: threshold }))
  }, [])

  return {
    results,
    total,
    sourcesStatus,
    loading,
    error,
    query: queries.join(', '),
    queries,
    filters,
    search,
    setFilters,
    updateSources,
    updateCategory,
    updateTimeRange,
    updateSemanticFilter,
    updateRelevanceThreshold,
    selectedIds,
    toggleSelect,
    selectAll,
    deselectAll,
    invertSelection,
    removeSelected,
    getSelectedResults,
  }
}
