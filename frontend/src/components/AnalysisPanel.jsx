import React, { useEffect } from 'react'
import { Drawer, Tabs, Typography, Spin, Tag, Empty, Button, Space, Divider, Alert } from 'antd'
import {
  FileTextOutlined,
  ExperimentOutlined,
} from '@ant-design/icons'

const { Text, Paragraph, Title } = Typography

export default function AnalysisPanel({
  visible,
  onClose,
  selectedItem,
  analysisResult,
  loading,
  activeTab,
  onTabChange,
  onSummarize,
  onAnalyzePaper,
  onAnalyzeFullPaper,
}) {
  useEffect(() => {
    if (visible && selectedItem && !analysisResult?.summary) {
      const content = selectedItem.snippet || selectedItem.title || ''
      if (content) onSummarize(content)
    }
  }, [visible, selectedItem])

  const renderSummary = () => {
    const data = analysisResult?.summary
    if (loading && !data) return <Spin tip="正在生成摘要..." />
    if (!data) return <Empty description="点击按钮生成摘要" />
    if (data.error) return <Text type="danger">错误: {data.error}</Text>

    return (
      <div>
        <Title level={5}>内容摘要</Title>
        <Paragraph>{data.summary || '暂无摘要'}</Paragraph>
        {data.key_points && data.key_points.length > 0 && (
          <>
            <Divider />
            <Title level={5}>关键要点</Title>
            <ul style={{ paddingLeft: 20 }}>
              {data.key_points.map((point, i) => (
                <li key={i} style={{ marginBottom: 4 }}>{point}</li>
              ))}
            </ul>
          </>
        )}
      </div>
    )
  }

  const renderPaperAnalysis = () => {
    const data = analysisResult?.paper
    const isAcademic = selectedItem?.category === 'academic'
    const isArxiv = selectedItem?.source === 'arxiv'
    const arxivId = selectedItem?.extra?.arxiv_id

    if (loading && !data) return <Spin tip="正在分析论文全文，请稍候..." />
    if (!data) {
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Space direction="vertical" size="middle">
            {isArxiv && arxivId && (
              <>
                <Button
                  type="primary"
                  icon={<ExperimentOutlined />}
                  onClick={() => onAnalyzeFullPaper(arxivId, selectedItem?.title || '')}
                >
                  深度分析论文全文
                </Button>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  将自动获取PDF全文并进行AI深度分析
                </Text>
              </>
            )}
            {isAcademic && !isArxiv && (
              <Button
                type="primary"
                icon={<ExperimentOutlined />}
                onClick={() =>
                  onAnalyzePaper({
                    title: selectedItem?.title || '',
                    abstract: selectedItem?.snippet || '',
                  })
                }
              >
                分析论文摘要
              </Button>
            )}
            {!isAcademic && (
              <Button type="primary" icon={<ExperimentOutlined />} disabled>
                仅支持学术论文
              </Button>
            )}
          </Space>
        </div>
      )
    }
    if (data.error) return <Text type="danger">错误: {data.error}</Text>

    const sections = [
      { key: 'abstract_summary', label: '摘要概述' },
      { key: 'method', label: '研究方法' },
      { key: 'innovation', label: '创新点' },
      { key: 'results', label: '实验结果' },
      { key: 'conclusion', label: '结论与局限性' },
    ]

    return (
      <div>
        {sections.map(
          ({ key, label }) =>
            data[key] && (
              <div key={key} style={{ marginBottom: 16 }}>
                <Title level={5}>{label}</Title>
                <Paragraph>{data[key]}</Paragraph>
              </div>
            )
        )}
      </div>
    )
  }

  const items = [
    {
      key: 'summary',
      label: <><FileTextOutlined /> 摘要</>,
      children: renderSummary(),
    },
    {
      key: 'paper',
      label: <><ExperimentOutlined /> 论文分析</>,
      children: renderPaperAnalysis(),
    },
  ]

  return (
    <Drawer
      title={
        <div style={{ maxWidth: 400 }}>
          <Text ellipsis>{selectedItem?.title || 'AI分析'}</Text>
        </div>
      }
      placement="right"
      width={480}
      open={visible}
      onClose={onClose}
    >
      {selectedItem && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Tag color="blue">{selectedItem.source}</Tag>
            <Tag>{selectedItem.category}</Tag>
          </Space>
        </div>
      )}
      <Tabs activeKey={activeTab} onChange={onTabChange} items={items} />
    </Drawer>
  )
}
