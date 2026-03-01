import { useState, useCallback, useEffect, useRef } from 'react'
import api from '../services/api'

function triggerBrowserDownload(downloadId) {
  const a = document.createElement('a')
  a.href = `/api/download/file/${downloadId}`
  a.download = ''
  a.style.display = 'none'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export default function useDownload() {
  const [downloads, setDownloads] = useState([])
  const [visible, setVisible] = useState(false)
  const pollingRef = useRef(null)
  const pendingAutoDownloadIds = useRef(new Set())

  const startDownload = useCallback(async (arxivId, title) => {
    try {
      const data = await api.post('/download/arxiv', {
        arxiv_id: arxivId,
        title,
      })
      const status = data.status || 'pending'
      setDownloads((prev) => [
        { id: data.download_id, title, status, file_size: 0, progress: status === 'completed' ? 100 : 0 },
        ...prev,
      ])
      setVisible(true)

      if (status === 'completed') {
        // Cache hit - trigger browser download immediately
        triggerBrowserDownload(data.download_id)
      } else {
        // Track for auto-download when completed
        pendingAutoDownloadIds.current.add(data.download_id)
      }

      return { id: data.download_id, status }
    } catch (err) {
      return null
    }
  }, [])

  const refreshStatus = useCallback(async () => {
    const pending = downloads.filter(
      (d) => d.status === 'pending' || d.status === 'downloading'
    )
    if (pending.length === 0) return

    // Batch update all pending downloads
    const updates = await Promise.allSettled(
      pending.map(async (d) => {
        try {
          const status = await api.get(`/download/status/${d.id}`)
          return { id: d.id, ...status }
        } catch {
          return null
        }
      })
    )

    const newlyCompleted = []

    setDownloads((curr) => {
      const newDownloads = [...curr]
      updates.forEach((result) => {
        if (result.status === 'fulfilled' && result.value) {
          const idx = newDownloads.findIndex((item) => item.id === result.value.id)
          if (idx !== -1) {
            const wasNotCompleted = newDownloads[idx].status !== 'completed'
            newDownloads[idx] = { ...newDownloads[idx], ...result.value }
            if (wasNotCompleted && result.value.status === 'completed') {
              newlyCompleted.push(result.value.id)
            }
          }
        }
      })
      return newDownloads
    })

    // Auto-trigger browser download for session-initiated downloads
    newlyCompleted.forEach((id) => {
      if (pendingAutoDownloadIds.current.has(id)) {
        triggerBrowserDownload(id)
        pendingAutoDownloadIds.current.delete(id)
      }
    })
  }, [downloads])

  // Poll for active downloads
  useEffect(() => {
    const hasActive = downloads.some(
      (d) => d.status === 'pending' || d.status === 'downloading'
    )
    if (hasActive && !pollingRef.current) {
      // Poll every 1.5 seconds for better progress updates
      pollingRef.current = setInterval(refreshStatus, 1500)
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
    pendingAutoDownloadIds.current.delete(id)
  }, [])

  return {
    downloads,
    visible,
    setVisible,
    startDownload,
    removeDownload,
  }
}
