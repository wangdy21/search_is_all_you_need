import React from 'react'
import { List, Progress, Badge, Typography, Button } from 'antd'
import {
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  UpOutlined,
  DownOutlined,
  DeleteOutlined,
} from '@ant-design/icons'

const { Text } = Typography

const STATUS_MAP = {
  pending: { icon: <LoadingOutlined />, color: '#1890ff', text: '等待中' },
  downloading: { icon: <LoadingOutlined spin />, color: '#1890ff', text: '下载中' },
  completed: { icon: <CheckCircleOutlined />, color: '#52c41a', text: '完成' },
  failed: { icon: <CloseCircleOutlined />, color: '#ff4d4f', text: '失败' },
}

export default function DownloadManager({ downloads, visible, onToggle, onRemove }) {
  if (downloads.length === 0) return null

  const activeCount = downloads.filter(
    (d) => d.status === 'pending' || d.status === 'downloading'
  ).length

  return (
    <div className="download-manager">
      <div className="download-manager-header" onClick={onToggle}>
        <span>
          <DownloadOutlined style={{ marginRight: 8 }} />
          下载管理
          {activeCount > 0 && (
            <Badge
              count={activeCount}
              size="small"
              style={{ marginLeft: 8, backgroundColor: '#fff', color: '#1890ff' }}
            />
          )}
        </span>
        {visible ? <UpOutlined /> : <DownOutlined />}
      </div>
      {visible && (
        <div className="download-manager-body">
          <List
            size="small"
            dataSource={downloads}
            renderItem={(item) => {
              const status = STATUS_MAP[item.status] || STATUS_MAP.pending
              return (
                <List.Item
                  style={{ padding: '8px 16px' }}
                  actions={[
                    item.status === 'completed' && (
                      <a
                        key="download"
                        href={`/api/download/file/${item.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <DownloadOutlined />
                      </a>
                    ),
                    <Button
                      key="remove"
                      type="text"
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => onRemove(item.id)}
                    />,
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    title={
                      <Text ellipsis style={{ maxWidth: 200, fontSize: 13 }}>
                        {item.title}
                      </Text>
                    }
                    description={
                      <div>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <span style={{ color: status.color }}>
                            {status.icon} {status.text}
                          </span>
                          {item.file_size > 0 && (
                            <span style={{ marginLeft: 8 }}>
                              {(item.file_size / 1024 / 1024).toFixed(1)} MB
                            </span>
                          )}
                        </Text>
                        {item.status === 'downloading' && (
                          <Progress
                            percent={50}
                            size="small"
                            status="active"
                            showInfo={false}
                            style={{ marginTop: 4 }}
                          />
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )
            }}
          />
        </div>
      )}
    </div>
  )
}
