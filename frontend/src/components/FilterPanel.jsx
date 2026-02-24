import React from 'react'
import { Card, Radio, Space, Typography } from 'antd'
import { FilterOutlined } from '@ant-design/icons'

const { Text } = Typography

const CATEGORIES = [
  { label: '全部', value: 'all' },
  { label: '学术论文', value: 'academic' },
  { label: '问答内容', value: 'qa' },
  { label: '博客文章', value: 'blog' },
  { label: '论坛帖子', value: 'forum' },
  { label: '网页', value: 'webpage' },
]

export default function FilterPanel({ filters, onCategoryChange, resultCounts }) {
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
      </Space>
    </Card>
  )
}
