import React, { useState, useEffect } from 'react'
import { Drawer, List, Typography, Button, Empty, Popconfirm } from 'antd'
import { HistoryOutlined, SearchOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../services/api'

const { Text } = Typography

export default function HistoryPanel({ visible, onClose, onSearch }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const data = await api.get('/history?limit=50')
      setHistory(data.history || [])
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (visible) fetchHistory()
  }, [visible])

  const clearHistory = async () => {
    try {
      await api.delete('/history')
      setHistory([])
    } catch {
      // ignore
    }
  }

  const handleClick = (query) => {
    onSearch(query)
    onClose()
  }

  return (
    <Drawer
      title={<><HistoryOutlined /> 搜索历史</>}
      placement="left"
      width={360}
      open={visible}
      onClose={onClose}
      extra={
        history.length > 0 && (
          <Popconfirm title="确定清空所有历史记录？" onConfirm={clearHistory}>
            <Button size="small" danger icon={<DeleteOutlined />}>
              清空
            </Button>
          </Popconfirm>
        )
      }
    >
      {history.length === 0 ? (
        <Empty description="暂无搜索历史" />
      ) : (
        <List
          loading={loading}
          dataSource={history}
          renderItem={(item) => (
            <List.Item
              style={{ cursor: 'pointer', padding: '8px 0' }}
              onClick={() => handleClick(item.query)}
              actions={[
                <Text type="secondary" style={{ fontSize: 11 }} key="count">
                  {item.result_count}条
                </Text>,
              ]}
            >
              <List.Item.Meta
                avatar={<SearchOutlined style={{ color: '#1890ff', fontSize: 16, marginTop: 4 }} />}
                title={<Text style={{ fontSize: 14 }}>{item.query}</Text>}
                description={
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    {item.timestamp?.replace('T', ' ').slice(0, 19)}
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Drawer>
  )
}
