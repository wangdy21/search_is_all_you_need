import React from 'react'
import { Card, Tag, Button, Space, Typography, Tooltip, Checkbox } from 'antd'
import {
  FileTextOutlined,
  TranslationOutlined,
  DownloadOutlined,
  LinkOutlined,
  UserOutlined,
  CalendarOutlined,
} from '@ant-design/icons'

const { Text } = Typography

const CATEGORY_COLORS = {
  academic: 'blue',
  qa: 'green',
  blog: 'orange',
  forum: 'purple',
  webpage: 'default',
}

const CATEGORY_LABELS = {
  academic: '学术论文',
  qa: '问答',
  blog: '博客',
  forum: '论坛',
  webpage: '网页',
}

const SOURCE_LABELS = {
  duckduckgo: 'DuckDuckGo',
  arxiv: 'arXiv',
  scholar: 'Scholar',
  zhihu: '知乎',
}

export default function ResultItem({ item, onAnalyze, onDownload, selected, onToggleSelect }) {
  const isArxiv = item.source === 'arxiv'
  const arxivId = item.extra?.arxiv_id

  return (
    <Card className="result-card" size="small">
      <div style={{ display: 'flex', gap: 12 }}>
        <div style={{ paddingTop: 4 }}>
          <Checkbox
            checked={selected}
            onChange={() => onToggleSelect(item._id)}
          />
        </div>
        <div style={{ flex: 1 }}>
          <div className="result-title">
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.title || '无标题'}
            </a>
          </div>

          <div className="result-snippet">
            {item.snippet || '暂无摘要'}
          </div>

          <div className="result-meta">
            <Tag color={CATEGORY_COLORS[item.category] || 'default'}>
              {CATEGORY_LABELS[item.category] || item.category}
            </Tag>
            <Tag>{SOURCE_LABELS[item.source] || item.source}</Tag>
            {item.authors && (
              <Tooltip title={item.authors}>
                <Text type="secondary">
                  <UserOutlined /> {item.authors.length > 30 ? item.authors.slice(0, 30) + '...' : item.authors}
                </Text>
              </Tooltip>
            )}
            {item.published && (
              <Text type="secondary">
                <CalendarOutlined /> {item.published.split('T')[0]}
              </Text>
            )}
            <Tooltip title={item.url}>
              <Text type="secondary">
                <LinkOutlined /> {new URL(item.url).hostname}
              </Text>
            </Tooltip>
          </div>

          <div className="result-actions">
            <Button
              size="small"
              icon={<FileTextOutlined />}
              onClick={() => onAnalyze(item)}
            >
              AI分析
            </Button>
            <Button
              size="small"
              icon={<TranslationOutlined />}
              onClick={() => {
                onAnalyze(item)
              }}
            >
              翻译
            </Button>
            {isArxiv && arxivId && (
              <Button
                size="small"
                type="primary"
                icon={<DownloadOutlined />}
                onClick={() => onDownload(arxivId, item.title)}
              >
                下载PDF
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
