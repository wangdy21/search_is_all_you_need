import React, { useState, useMemo } from 'react'
import { Layout, Button, message } from 'antd'
import { HistoryOutlined } from '@ant-design/icons'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import ResultList from './components/ResultList'
import AnalysisPanel from './components/AnalysisPanel'
import DownloadManager from './components/DownloadManager'
import HistoryPanel from './components/HistoryPanel'
import useSearch from './hooks/useSearch'
import useAnalysis from './hooks/useAnalysis'
import useDownload from './hooks/useDownload'

const { Header, Content } = Layout

export default function App() {
  const [historyVisible, setHistoryVisible] = useState(false)

  const {
    results,
    total,
    sourcesStatus,
    loading: searchLoading,
    filters,
    search,
    updateSources,
    updateCategory,
    updateTimeRange,
  } = useSearch()

  const {
    analysisResult,
    loading: analysisLoading,
    visible: analysisVisible,
    selectedItem,
    activeTab,
    setActiveTab,
    summarize,
    translate,
    analyzePaper,
    openAnalysis,
    closeAnalysis,
  } = useAnalysis()

  const {
    downloads,
    visible: downloadVisible,
    setVisible: setDownloadVisible,
    startDownload,
    removeDownload,
  } = useDownload()

  const handleDownload = async (arxivId, title) => {
    const id = await startDownload(arxivId, title)
    if (id) {
      message.success('下载任务已创建')
    }
  }

  // Compute category counts for filter panel
  const resultCounts = useMemo(() => {
    const counts = { all: total }
    ;(results || []).forEach((item) => {
      const cat = item.category || 'webpage'
      counts[cat] = (counts[cat] || 0) + 1
    })
    return counts
  }, [results, total])

  // Apply client-side category filter
  const filteredResults = useMemo(() => {
    if (!filters.category || filters.category === 'all') return results
    return results.filter((item) => item.category === filters.category)
  }, [results, filters.category])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="app-header">
        <h1>Search Is All You Need</h1>
        <div style={{ flex: 1 }}>
          <SearchBar
            onSearch={search}
            sources={filters.sources}
            onSourcesChange={updateSources}
            loading={searchLoading}
            timeRange={filters.time_range}
            onTimeRangeChange={updateTimeRange}
          />
        </div>
        <Button
          type="text"
          icon={<HistoryOutlined />}
          onClick={() => setHistoryVisible(true)}
          style={{ color: '#fff' }}
        >
          历史
        </Button>
      </Header>

      <Content className="app-content">
        <div className="results-section">
          <div className="results-main">
            <ResultList
              results={filteredResults}
              total={total}
              loading={searchLoading}
              sourcesStatus={sourcesStatus}
              onAnalyze={openAnalysis}
              onDownload={handleDownload}
            />
          </div>
          {results.length > 0 && (
            <div className="results-sidebar">
              <FilterPanel
                filters={filters}
                onCategoryChange={updateCategory}
                resultCounts={resultCounts}
              />
            </div>
          )}
        </div>
      </Content>

      <AnalysisPanel
        visible={analysisVisible}
        onClose={closeAnalysis}
        selectedItem={selectedItem}
        analysisResult={analysisResult}
        loading={analysisLoading}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onSummarize={summarize}
        onTranslate={translate}
        onAnalyzePaper={analyzePaper}
      />

      <DownloadManager
        downloads={downloads}
        visible={downloadVisible}
        onToggle={() => setDownloadVisible((v) => !v)}
        onRemove={removeDownload}
      />

      <HistoryPanel
        visible={historyVisible}
        onClose={() => setHistoryVisible(false)}
        onSearch={search}
      />
    </Layout>
  )
}
