import React, { useState } from 'react'
import { List, Spin, Empty, Typography, Button, Space, Divider, message, Modal, Progress, Card, Badge } from 'antd'
import {
  CheckSquareOutlined,
  BorderOutlined,
  SwapOutlined,
  DeleteOutlined,
  ExportOutlined,
  SearchOutlined,
  DatabaseOutlined,
} from '@ant-design/icons'
import ResultItem from './ResultItem'
import api from '../services/api'

const { Text } = Typography

export default function ResultList({
  results,
  total,
  loading,
  sourcesStatus,
  onAnalyze,
  onDownload,
  selectedIds,
  onToggleSelect,
  onSelectAll,
  onDeselectAll,
  onInvertSelection,
  onRemoveSelected,
  getSelectedResults,
}) {
  const [exporting, setExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)

  const handleExport = async () => {
    const selected = getSelectedResults()
    if (selected.length === 0) {
      message.warning('请先选择要导出的结果')
      return
    }

    setExporting(true)
    setExportProgress(0)

    try {
      // Translate snippets to Chinese via backend API
      const translatedResults = []
      for (let i = 0; i < selected.length; i++) {
        const item = selected[i]
        let translatedSnippet = item.snippet || ''

        // Only translate if snippet contains non-Chinese characters
        if (translatedSnippet && !/^[\u4e00-\u9fa5\s\d，。！？、：；""''（）【】《》]+$/.test(translatedSnippet)) {
          try {
            const response = await api.post('/translate', {
              text: translatedSnippet,
              target_lang: 'zh',
            })
            translatedSnippet = response.translated || translatedSnippet
          } catch (err) {
            console.warn('Translation failed for item:', item.title, err)
          }
        }

        translatedResults.push({
          title: item.title || '',
          snippet: translatedSnippet,
          url: item.url || '',
        })

        setExportProgress(Math.round(((i + 1) / selected.length) * 100))
      }

      // Generate CSV content
      const csvHeader = '\uFEFF标题,内容摘要,原始链接\n'
      const csvRows = translatedResults.map((item) => {
        const title = `"${(item.title || '').replace(/"/g, '""')}"`
        const snippet = `"${(item.snippet || '').replace(/"/g, '""')}"`
        const url = `"${(item.url || '').replace(/"/g, '""')}"`
        return `${title},${snippet},${url}`
      }).join('\n')

      const csvContent = csvHeader + csvRows

      // Download CSV file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `search_results_${new Date().toISOString().slice(0, 10)}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      message.success(`成功导出 ${translatedResults.length} 条结果`)
    } catch (err) {
      message.error('导出失败: ' + (err.message || '未知错误'))
    } finally {
      setExporting(false)
      setExportProgress(0)
    }
  }

  if (loading) {
    return (
      <Card className="loading-card">
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" tip="正在搜索中..." />
        </div>
      </Card>
    )
  }

  if (!results || results.length === 0) {
    return (
      <Card className="empty-card">
        <Empty 
          description="暂无搜索结果" 
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    )
  }

  const selectedCount = selectedIds?.size || 0

  return (
    <div className="result-list-container">
      {/* 统计信息栏 */}
      <Card className="stats-card" size="small">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <Space size="middle">
            <Badge 
              count={total} 
              showZero 
              color="#1890ff"
              style={{ fontSize: 12 }}
            >
              <Text type="secondary">
                <SearchOutlined style={{ marginRight: 4 }} />
                搜索结果
              </Text>
            </Badge>
            <Text type="secondary" style={{ fontSize: 12 }}>
              显示 {results.length} 条
            </Text>
          </Space>
          
          {sourcesStatus && (
            <Space size="small" wrap>
              {Object.entries(sourcesStatus).map(([src, status]) => (
                <Badge
                  key={src}
                  status={status === 'success' ? 'success' : status === 'timeout' ? 'warning' : 'error'}
                  text={
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      {src}
                    </Text>
                  }
                />
              ))}
            </Space>
          )}
        </div>
      </Card>

      {/* 操作工具栏 */}
      <Card className="toolbar-card" size="small">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <Space size="small" wrap>
            <Text type="secondary" style={{ fontSize: 13 }}>
              <DatabaseOutlined style={{ marginRight: 4 }} />
              已选择 <Text strong type="primary">{selectedCount}</Text> 项
            </Text>
            <Divider type="vertical" style={{ margin: '0 4px' }} />
            <Button
              size="small"
              icon={<CheckSquareOutlined />}
              onClick={onSelectAll}
            >
              全选
            </Button>
            <Button
              size="small"
              icon={<BorderOutlined />}
              onClick={onDeselectAll}
            >
              取消
            </Button>
            <Button
              size="small"
              icon={<SwapOutlined />}
              onClick={onInvertSelection}
            >
              反选
            </Button>
            <Button
              size="small"
              icon={<DeleteOutlined />}
              danger
              onClick={onRemoveSelected}
              disabled={selectedCount === 0}
            >
              删除
            </Button>
          </Space>
          
          <Button
            size="small"
            icon={<ExportOutlined />}
            type="primary"
            onClick={handleExport}
            loading={exporting}
            disabled={selectedCount === 0}
          >
            导出选中结果
          </Button>
        </div>
        
        {exporting && (
          <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Text type="secondary" style={{ fontSize: 12 }}>
                正在翻译并导出... {exportProgress}%
              </Text>
              <Progress percent={exportProgress} size="small" status="active" />
            </Space>
          </div>
        )}
      </Card>

      <List
        dataSource={results}
        renderItem={(item, index) => (
          <ResultItem
            key={item._id || item.url || index}
            item={item}
            onAnalyze={onAnalyze}
            onDownload={onDownload}
            selected={selectedIds?.has(item._id)}
            onToggleSelect={onToggleSelect}
          />
        )}
      />
    </div>
  )
}
