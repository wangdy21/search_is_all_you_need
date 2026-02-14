import React from 'react'
import { List, Spin, Empty, Typography } from 'antd'
import ResultItem from './ResultItem'

const { Text } = Typography

export default function ResultList({
  results,
  total,
  loading,
  sourcesStatus,
  onAnalyze,
  onDownload,
}) {
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

  return (
    <div>
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between' }}>
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
      <List
        dataSource={results}
        renderItem={(item, index) => (
          <ResultItem
            key={item.url || index}
            item={item}
            onAnalyze={onAnalyze}
            onDownload={onDownload}
          />
        )}
      />
    </div>
  )
}
