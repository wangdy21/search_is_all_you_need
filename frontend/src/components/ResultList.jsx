import React, { useState } from 'react'
import { List, Spin, Empty, Typography, Button, Space, Divider, message, Modal, Progress } from 'antd'
import {
  CheckSquareOutlined,
  BorderOutlined,
  SwapOutlined,
  DeleteOutlined,
  ExportOutlined,
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
      <div style={{ textAlign: 'center', padding: 60 }}>
        <Spin size="large" tip="正在搜索中..." />
      </div>
    )
  }

  if (!results || results.length === 0) {
    return <Empty description="暂无搜索结果" style={{ padding: 60 }} />
  }

  const selectedCount = selectedIds?.size || 0

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text type="secondary">
          共找到 <Text strong>{total}</Text> 条结果
          （当前显示 {results.length} 条）
        </Text>
        {sourcesStatus && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {Object.entries(sourcesStatus).map(([src, status]) => (
              <span key={src} style={{ marginLeft: 8 }}>
                {src}: {status === 'success' ? '✓' : '✗'}
              </span>
            ))}
          </Text>
        )}
      </div>

      <div style={{ marginBottom: 16, padding: '12px 16px', background: '#f5f5f5', borderRadius: 8 }}>
        <Space split={<Divider type="vertical" />} wrap>
          <Text type="secondary">
            已选择 <Text strong type="primary">{selectedCount}</Text> 项
          </Text>
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
            取消全选
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
            删除选中项
          </Button>
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
        </Space>
        {exporting && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>正在翻译并导出...</Text>
            <Progress percent={exportProgress} size="small" />
          </div>
        )}
      </div>

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
