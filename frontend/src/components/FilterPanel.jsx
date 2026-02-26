import React from 'react'
import { Card, Radio, Space, Typography, Switch, Slider, Divider, Tooltip } from 'antd'
import { FilterOutlined, RobotOutlined, QuestionCircleOutlined } from '@ant-design/icons'

const { Text } = Typography

const CATEGORIES = [
  { label: '全部', value: 'all' },
  { label: '学术论文', value: 'academic' },
  { label: '问答内容', value: 'qa' },
  { label: '博客文章', value: 'blog' },
  { label: '论坛帖子', value: 'forum' },
  { label: '网页', value: 'webpage' },
]

const THRESHOLD_MARKS = {
  0: '0',
  40: '40',
  60: '60',
  80: '80',
  100: '100',
}

export default function FilterPanel({
  filters,
  onCategoryChange,
  onSemanticFilterChange,
  onRelevanceThresholdChange,
  resultCounts,
}) {
  const counts = resultCounts || {}

  return (
    <Card
      size="small"
      title={<><FilterOutlined /> 筛选条件</>}
      style={{ marginBottom: 16 }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <Text type="secondary" style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>
            内容分类
          </Text>
          <Radio.Group
            value={filters.category}
            onChange={(e) => onCategoryChange(e.target.value)}
            size="small"
            style={{ display: 'flex', flexDirection: 'column', gap: 4 }}
          >
            {CATEGORIES.map((cat) => (
              <Radio key={cat.value} value={cat.value}>
                {cat.label}
                {counts[cat.value] !== undefined && (
                  <Text type="secondary" style={{ marginLeft: 4 }}>
                    ({counts[cat.value]})
                  </Text>
                )}
              </Radio>
            ))}
          </Radio.Group>
        </div>

        <Divider style={{ margin: '8px 0' }} />

        <div>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <RobotOutlined style={{ marginRight: 6, color: '#1890ff' }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              AI 语义过滤
            </Text>
            <Tooltip title="启用后，AI 会评估每个结果与搜索词的语义相关性，过滤掉不相关的内容">
              <QuestionCircleOutlined style={{ marginLeft: 4, color: '#999', cursor: 'help' }} />
            </Tooltip>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Text style={{ fontSize: 13 }}>启用语义过滤</Text>
            <Switch
              size="small"
              checked={filters.semantic_filter}
              onChange={onSemanticFilterChange}
            />
          </div>
        </div>

        {filters.semantic_filter && (
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
              相关性阈值: <Text strong>{filters.relevance_threshold}</Text>
            </Text>
            <Slider
              min={0}
              max={100}
              step={5}
              marks={THRESHOLD_MARKS}
              value={filters.relevance_threshold}
              onChange={onRelevanceThresholdChange}
              tooltip={{ formatter: (val) => `${val}分` }}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              分数越高过滤越严格，建议值: 40-60
            </Text>
          </div>
        )}
      </Space>
    </Card>
  )
}
