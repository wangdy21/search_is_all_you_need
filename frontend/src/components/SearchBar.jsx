import React from 'react'
import { Input, Checkbox, Radio, Space } from 'antd'
import { SearchOutlined, ClockCircleOutlined } from '@ant-design/icons'

const SOURCE_OPTIONS = [
  { label: 'DuckDuckGo', value: 'duckduckgo' },
  { label: 'arXiv', value: 'arxiv' },
  { label: 'Google Scholar', value: 'scholar' },
  { label: '知乎', value: 'zhihu' },
]

const TIME_RANGES = [
  { label: '不限', value: null },
  { label: '近一周', value: 'week' },
  { label: '近一月', value: 'month' },
  { label: '近一年', value: 'year' },
  { label: '近三年', value: '3years' },
]

export default function SearchBar({ onSearch, sources, onSourcesChange, loading, timeRange, onTimeRangeChange }) {
  const handleSearch = (value) => {
    if (value.trim()) {
      onSearch(value.trim())
    }
  }

  return (
    <div className="search-section">
      <Input.Search
        placeholder="输入关键词搜索全网内容..."
        enterButton={<><SearchOutlined /> 搜索</>}
        size="large"
        allowClear
        loading={loading}
        onSearch={handleSearch}
        style={{ marginBottom: 12 }}
      />
      <Space wrap>
        <span style={{ color: '#fff', fontSize: 13 }}>搜索源：</span>
        <Checkbox.Group
          options={SOURCE_OPTIONS}
          value={sources}
          onChange={onSourcesChange}
          style={{ color: '#fff' }}
        />
        <span style={{ color: '#fff', fontSize: 13, marginLeft: 12 }}>
          <ClockCircleOutlined /> 时间范围：
        </span>
        <Radio.Group
          value={timeRange === undefined ? null : timeRange}
          onChange={(e) => onTimeRangeChange(e.target.value)}
          size="small"
          optionType="button"
          buttonStyle="solid"
        >
          {TIME_RANGES.map((tr) => (
            <Radio.Button key={String(tr.value)} value={tr.value} style={{ fontSize: 12 }}>
              {tr.label}
            </Radio.Button>
          ))}
        </Radio.Group>
      </Space>
    </div>
  )
}
