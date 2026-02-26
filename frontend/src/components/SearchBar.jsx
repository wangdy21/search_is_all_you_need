import React, { useState } from 'react'
import { Input, Checkbox, Radio, Space, Button, Row, Col } from 'antd'
import { SearchOutlined, ClockCircleOutlined, PlusOutlined, MinusOutlined } from '@ant-design/icons'

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

const MAX_KEYWORDS = 5

export default function SearchBar({ onSearch, sources, onSourcesChange, loading, timeRange, onTimeRangeChange }) {
  const [keywords, setKeywords] = useState([''])

  const handleKeywordChange = (index, value) => {
    const newKeywords = [...keywords]
    newKeywords[index] = value
    setKeywords(newKeywords)
  }

  const addKeywordInput = () => {
    if (keywords.length < MAX_KEYWORDS) {
      setKeywords([...keywords, ''])
    }
  }

  const removeKeywordInput = (index) => {
    if (keywords.length > 1) {
      const newKeywords = keywords.filter((_, i) => i !== index)
      setKeywords(newKeywords)
    }
  }

  const handleSearch = () => {
    const validKeywords = keywords.map(k => k.trim()).filter(k => k.length > 0)
    if (validKeywords.length > 0) {
      onSearch(validKeywords)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="search-section">
      <div style={{ marginBottom: 12 }}>
        {keywords.map((keyword, index) => (
          <Row key={index} gutter={8} style={{ marginBottom: 8 }}>
            <Col flex="auto">
              <Input
                placeholder={`关键词 ${index + 1}`}
                value={keyword}
                onChange={(e) => handleKeywordChange(index, e.target.value)}
                onKeyPress={handleKeyPress}
                size="large"
                allowClear
              />
            </Col>
            <Col flex="none">
              {keywords.length > 1 && (
                <Button
                  icon={<MinusOutlined />}
                  onClick={() => removeKeywordInput(index)}
                  size="large"
                  danger
                />
              )}
            </Col>
          </Row>
        ))}
        <Space style={{ marginTop: 8 }}>
          {keywords.length < MAX_KEYWORDS && (
            <Button
              icon={<PlusOutlined />}
              onClick={addKeywordInput}
              size="small"
            >
              添加关键词
            </Button>
          )}
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
            size="large"
          >
            搜索
          </Button>
        </Space>
      </div>
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
