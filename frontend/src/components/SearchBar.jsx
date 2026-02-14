import React from 'react'
import { Input, Checkbox, Space } from 'antd'
import { SearchOutlined } from '@ant-design/icons'

const SOURCE_OPTIONS = [
  { label: 'DuckDuckGo', value: 'duckduckgo' },
  { label: 'arXiv', value: 'arxiv' },
  { label: 'Google Scholar', value: 'scholar' },
  { label: '知乎', value: 'zhihu' },
]

export default function SearchBar({ onSearch, sources, onSourcesChange, loading }) {
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
      <Space>
        <span style={{ color: '#fff', fontSize: 13 }}>搜索源：</span>
        <Checkbox.Group
          options={SOURCE_OPTIONS}
          value={sources}
          onChange={onSourcesChange}
          style={{ color: '#fff' }}
        />
      </Space>
    </div>
  )
}
