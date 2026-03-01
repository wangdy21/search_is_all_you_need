import React, { useState } from 'react'
import { Input, Checkbox, Radio, Space, Button, Row, Col, Card, Tooltip, Tag, Divider } from 'antd'
import { 
  SearchOutlined, 
  ClockCircleOutlined, 
  PlusOutlined, 
  MinusOutlined,
  KeyOutlined,
  GlobalOutlined,
  FireOutlined
} from '@ant-design/icons'

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

// 搜索源图标映射
const SOURCE_ICONS = {
  duckduckgo: <GlobalOutlined />,
  arxiv: <FireOutlined style={{ color: '#b31b1b' }} />,
  scholar: <FireOutlined style={{ color: '#4285f4' }} />,
  zhihu: <FireOutlined style={{ color: '#0084ff' }} />,
}

export default function SearchBar({ onSearch, sources, onSourcesChange, loading, timeRange, onTimeRangeChange }) {
  const [keywords, setKeywords] = useState([''])
  const [isFocused, setIsFocused] = useState(false)

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
      {/* 关键词输入区域 */}
      <Card 
        className={`search-keywords-card ${isFocused ? 'focused' : ''}`}
        size="small"
        style={{ 
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 12,
          border: 'none',
          boxShadow: isFocused 
            ? '0 8px 24px rgba(24, 144, 255, 0.25)' 
            : '0 4px 12px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.3s ease',
          marginBottom: 16
        }}
        styles={{ body: { padding: '16px 20px' } }}
      >
        <div style={{ marginBottom: 12 }}>
          <Space align="center" style={{ marginBottom: 12 }}>
            <KeyOutlined style={{ color: '#1890ff', fontSize: 16 }} />
            <span style={{ fontWeight: 500, color: '#333' }}>搜索关键词</span>
            <Tag color="blue" style={{ marginLeft: 8 }}>
              {keywords.filter(k => k.trim()).length}/{MAX_KEYWORDS}
            </Tag>
          </Space>
          
          {keywords.map((keyword, index) => (
            <Row key={index} gutter={12} style={{ marginBottom: 10 }}>
              <Col flex="auto">
                <Input
                  placeholder={`输入关键词 ${index + 1}...`}
                  value={keyword}
                  onChange={(e) => handleKeywordChange(index, e.target.value)}
                  onKeyPress={handleKeyPress}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  size="large"
                  allowClear
                  prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
                  style={{ 
                    borderRadius: 8,
                    fontSize: 15
                  }}
                />
              </Col>
              <Col flex="none">
                {keywords.length > 1 && (
                  <Tooltip title="移除此关键词">
                    <Button
                      icon={<MinusOutlined />}
                      onClick={() => removeKeywordInput(index)}
                      size="large"
                      danger
                      type="text"
                      style={{ borderRadius: 8 }}
                    />
                  </Tooltip>
                )}
              </Col>
            </Row>
          ))}
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            {keywords.length < MAX_KEYWORDS && (
              <Button
                icon={<PlusOutlined />}
                onClick={addKeywordInput}
                size="middle"
                type="dashed"
                style={{ borderRadius: 6 }}
              >
                添加关键词
              </Button>
            )}
          </Space>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
            size="large"
            style={{ 
              borderRadius: 8,
              paddingLeft: 24,
              paddingRight: 24,
              height: 44,
              fontWeight: 500,
              boxShadow: '0 4px 12px rgba(24, 144, 255, 0.35)'
            }}
          >
            开始搜索
          </Button>
        </div>
      </Card>

      {/* 搜索选项区域 */}
      <div className="search-options" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        flexWrap: 'wrap',
        gap: 16
      }}>
        {/* 搜索源 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <GlobalOutlined style={{ color: 'rgba(255,255,255,0.85)', fontSize: 14 }} />
          <span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 13, fontWeight: 500 }}>搜索源：</span>
          <Checkbox.Group
            value={sources}
            onChange={onSourcesChange}
            style={{ marginLeft: 4 }}
          >
            {SOURCE_OPTIONS.map(opt => (
              <Checkbox 
                key={opt.value} 
                value={opt.value}
                style={{ 
                  color: 'rgba(255,255,255,0.85)',
                  fontSize: 13
                }}
              >
                <Space size={4}>
                  {SOURCE_ICONS[opt.value]}
                  {opt.label}
                </Space>
              </Checkbox>
            ))}
          </Checkbox.Group>
        </div>

        <Divider type="vertical" style={{ borderColor: 'rgba(255,255,255,0.3)', height: 20 }} />

        {/* 时间范围 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ClockCircleOutlined style={{ color: 'rgba(255,255,255,0.85)', fontSize: 14 }} />
          <span style={{ color: 'rgba(255,255,255,0.9)', fontSize: 13, fontWeight: 500 }}>时间：</span>
          <Radio.Group
            value={timeRange === undefined ? null : timeRange}
            onChange={(e) => onTimeRangeChange(e.target.value)}
            size="small"
            optionType="button"
            buttonStyle="solid"
          >
            {TIME_RANGES.map((tr) => (
              <Radio.Button 
                key={String(tr.value)} 
                value={tr.value} 
                style={{ 
                  fontSize: 12,
                  borderRadius: 4
                }}
              >
                {tr.label}
              </Radio.Button>
            ))}
          </Radio.Group>
        </div>
      </div>
    </div>
  )
}
