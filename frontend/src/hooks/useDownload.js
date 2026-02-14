import { useState, useCallback, useEffect, useRef } from 'react'
import api from '../services/api'

export default function useDownload() {
  const [downloads, setDownloads] = useState([])
  const [visible, setVisible] = useState(false)
  const pollingRef = useRef(null)

  const startDownload = useCallback(async (arxivId, title) => {
    try {
      const data = await api.post('/download/arxiv', {
        arxiv_id: arxivId,
        title,
      })
      setDownloads((prev) => [
        { id: data.download_id, title, status: 'pending', file_size: 0 },
        ...prev,
      ])
      setVisible(true)
      return data.download_id
    } catch (err) {
      return null
    }
  }, [])

  const refreshStatus = useCallback(async () => {
    setDownloads((prev) => {
      const pending = prev.filter(
        (d) => d.status === 'pending' || d.status === 'downloading'
      )
      if (pending.length === 0) return prev

      // Update each pending download
      pending.forEach(async (d) => {
        try {
          const status = await api.get(`/download/status/${d.id}`)
          setDownloads((curr) =>
            curr.map((item) =>
              item.id === d.id ? { ...item, ...status } : item
            )
          )
        } catch {
          // ignore polling errors
        }
      })
      return prev
    })
  }, [])

  // Poll for active downloads
  useEffect(() => {
    const hasActive = downloads.some(
      (d) => d.status === 'pending' || d.status === 'downloading'
    )
    if (hasActive && !pollingRef.current) {
      pollingRef.current = setInterval(refreshStatus, 2000)
    } else if (!hasActive && pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [downloads, refreshStatus])

  const removeDownload = useCallback((id) => {
    setDownloads((prev) => prev.filter((d) => d.id !== id))
  }, [])

  return {
    downloads,
    visible,
    setVisible,
    startDownload,
    removeDownload,
  }
}
