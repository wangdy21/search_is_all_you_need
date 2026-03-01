import { useState, useCallback } from 'react'
import api from '../services/api'

export default function useAnalysis() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [visible, setVisible] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [activeTab, setActiveTab] = useState('summary')

  const summarize = useCallback(async (content) => {
    setLoading(true)
    try {
      const data = await api.post('/analysis/summarize', { content })
      setAnalysisResult((prev) => ({ ...prev, summary: data }))
    } catch (err) {
      setAnalysisResult((prev) => ({
        ...prev,
        summary: { error: err.message || 'Summarize failed' },
      }))
    } finally {
      setLoading(false)
    }
  }, [])

  const analyzePaper = useCallback(async (paperData) => {
    setLoading(true)
    try {
      const data = await api.post('/analysis/paper', paperData)
      setAnalysisResult((prev) => ({ ...prev, paper: data }))
    } catch (err) {
      setAnalysisResult((prev) => ({
        ...prev,
        paper: { error: err.message || 'Paper analysis failed' },
      }))
    } finally {
      setLoading(false)
    }
  }, [])

  const analyzeFullPaper = useCallback(async (arxivId, title) => {
    setLoading(true)
    try {
      const data = await api.post('/analysis/paper-full', {
        arxiv_id: arxivId,
        title,
      }, { timeout: 180000 })
      setAnalysisResult((prev) => ({ ...prev, paper: data }))
    } catch (err) {
      setAnalysisResult((prev) => ({
        ...prev,
        paper: { error: err.message || 'Full paper analysis failed' },
      }))
    } finally {
      setLoading(false)
    }
  }, [])

  const openAnalysis = useCallback((item) => {
    setSelectedItem(item)
    setAnalysisResult(null)
    setActiveTab('summary')
    setVisible(true)
  }, [])

  const closeAnalysis = useCallback(() => {
    setVisible(false)
    setSelectedItem(null)
    setAnalysisResult(null)
  }, [])

  return {
    analysisResult,
    loading,
    visible,
    selectedItem,
    activeTab,
    setActiveTab,
    summarize,
    analyzePaper,
    analyzeFullPaper,
    openAnalysis,
    closeAnalysis,
  }
}
