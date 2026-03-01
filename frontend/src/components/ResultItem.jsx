import React from 'react'
import { Card, Tag, Button, Space, Typography, Tooltip, Checkbox, Badge } from 'antd'
import {
  FileTextOutlined,
  TranslationOutlined,
  DownloadOutlined,
  LinkOutlined,
  UserOutlined,
  CalendarOutlined,
  RobotOutlined,
  GlobalOutlined,
} from '@ant-design/icons'

const { Text } = Typography

const CATEGORY_COLORS = {
  academic: 'processing',
  qa: 'success',
  blog: 'warning',
  forum: 'purple',
  webpage: 'default',
}

const CATEGORY_ICONS = {
  academic: <FileTextOutlined />,
  qa: <RobotOutlined />,
  blog: <GlobalOutlined />,
  forum: <RobotOutlined />,
  webpage: <GlobalOutlined />,
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
    <Card 
      className="result-card" 
      size="small"
      styles={{ body: { padding: '16px' } }}
    >
      <div style={{ display: 'flex', gap: 12 }}>
        <div style={{ paddingTop: 4 }}>
          <Checkbox
            checked={selected}
            onChange={() => onToggleSelect(item._id)}
          />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* 标题区域 */}
          <div className="result-title">
            <Space>
              <Tooltip title={CATEGORY_LABELS[item.category] || item.category}>
                <span style={{ color: 'var(--ant-color-primary)' }}>
                  {CATEGORY_ICONS[item.category] || <GlobalOutlined />}
                </span>
              </Tooltip>
              <a 
                href={item.url} 
                target="_blank" 
                rel="noopener noreferrer"
                title={item.title}
              >
                {item.title || '无标题'}
              </a>
            </Space>
          </div>

          {/* 摘要区域 */}
          <div className="result-snippet">
            {item.snippet || '暂无摘要'}
          </div>

          {/* 元信息区域 */}
          <div className="result-meta">
            <Badge 
              color={CATEGORY_COLORS[item.category] || 'default'}
              text={
                <Tag color={CATEGORY_COLORS[item.category] || 'default'} style={{ margin: 0 }}>
                  {CATEGORY_LABELS[item.category] || item.category}
                </Tag>
              }
            />
            <Tag color="processing" style={{ fontSize: 11 }}>
              {SOURCE_LABELS[item.source] || item.source}
            </Tag>
            {item.authors && (
              <Tooltip title={item.authors}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  <UserOutlined style={{ marginRight: 4 }} />
                  {item.authors.length > 25 ? item.authors.slice(0, 25) + '...' : item.authors}
                </Text>
              </Tooltip>
            )}
            {item.published && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                <CalendarOutlined style={{ marginRight: 4 }} />
                {item.published.split('T')[0]}
              </Text>
            )}
            <Tooltip title={item.url}>
              <Text type="secondary" style={{ fontSize: 12 }} className="hostname-text">
                <LinkOutlined style={{ marginRight: 4 }} />
                {new URL(item.url).hostname}
              </Text>
            </Tooltip>
          </div>

          {/* 操作按钮区域 */}
          <div className="result-actions">
            <Space size="small" wrap>
              <Button
                size="small"
                icon={<RobotOutlined />}
                onClick={() => onAnalyze(item)}
              >
                AI分析
              </Button>
              <Button
                size="small"
                icon={<TranslationOutlined />}
                onClick={() => onAnalyze(item)}
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
            </Space>
          </div>
        </div>
      </div>
    </Card>
  )
}
