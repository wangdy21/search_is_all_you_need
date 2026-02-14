import React, { useEffect } from 'react'
import { Drawer, Tabs, Typography, Spin, Tag, Empty, Button, Space, Divider } from 'antd'
import {
  FileTextOutlined,
  TranslationOutlined,
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
  onTranslate,
  onAnalyzePaper,
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

  const renderTranslation = () => {
    const data = analysisResult?.translation
    if (loading && !data) return <Spin tip="正在翻译..." />
    if (!data) {
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Button
            type="primary"
            icon={<TranslationOutlined />}
            onClick={() => onTranslate(selectedItem?.snippet || selectedItem?.title || '')}
          >
            翻译为中文
          </Button>
        </div>
      )
    }
    if (data.error) return <Text type="danger">错误: {data.error}</Text>

    return (
      <div>
        <Title level={5}>翻译结果</Title>
        <Paragraph>{data.translated_text}</Paragraph>
      </div>
    )
  }

  const renderPaperAnalysis = () => {
    const data = analysisResult?.paper
    if (loading && !data) return <Spin tip="正在分析论文..." />
    if (!data) {
      const isAcademic = selectedItem?.category === 'academic'
      return (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Button
            type="primary"
            icon={<ExperimentOutlined />}
            disabled={!isAcademic}
            onClick={() =>
              onAnalyzePaper({
                title: selectedItem?.title || '',
                abstract: selectedItem?.snippet || '',
              })
            }
          >
            {isAcademic ? '深度分析论文' : '仅支持学术论文'}
          </Button>
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
      key: 'translation',
      label: <><TranslationOutlined /> 翻译</>,
      children: renderTranslation(),
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
