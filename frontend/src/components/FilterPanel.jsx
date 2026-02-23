import React from 'react'
import { Card, Radio, Space, Typography } from 'antd'
import { FilterOutlined, ClockCircleOutlined } from '@ant-design/icons'

const { Text } = Typography

const CATEGORIES = [
  { label: '全部', value: 'all' },
  { label: '学术论文', value: 'academic' },
  { label: '问答内容', value: 'qa' },
  { label: '博客文章', value: 'blog' },
  { label: '论坛帖子', value: 'forum' },
  { label: '网页', value: 'webpage' },
]

const TIME_RANGES = [
  { label: '不限', value: null },
  { label: '近一周', value: 'week' },
  { label: '近一月', value: 'month' },
  { label: '近一年', value: 'year' },
  { label: '近三年', value: '3years' },
]

export default function FilterPanel({ filters, onCategoryChange, onTimeRangeChange, resultCounts }) {
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

        <div>
          <Text type="secondary" style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>
            <ClockCircleOutlined /> 时间范围
          </Text>
          <Radio.Group
            value={filters.time_range === undefined ? null : filters.time_range}
            onChange={(e) => onTimeRangeChange(e.target.value)}
            size="small"
            optionType="button"
            buttonStyle="solid"
            style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}
          >
            {TIME_RANGES.map((tr) => (
              <Radio.Button key={String(tr.value)} value={tr.value} style={{ fontSize: 12 }}>
                {tr.label}
              </Radio.Button>
            ))}
          </Radio.Group>
        </div>
      </Space>
    </Card>
  )
}
