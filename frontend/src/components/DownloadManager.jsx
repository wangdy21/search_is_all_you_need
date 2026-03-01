import React from 'react'
import { List, Progress, Badge, Typography, Button, Space, Tag, Tooltip, Card } from 'antd'
import {
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  UpOutlined,
  DownOutlined,
  DeleteOutlined,
  CloudDownloadOutlined,
  FileOutlined,
  ClockCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'

const { Text } = Typography

const STATUS_MAP = {
  pending: { 
    icon: <ClockCircleOutlined />, 
    color: '#faad14', 
    bgColor: 'rgba(250, 173, 20, 0.1)',
    text: '等待中',
    tagColor: 'warning'
  },
  downloading: { 
    icon: <SyncOutlined spin />, 
    color: '#1890ff', 
    bgColor: 'rgba(24, 144, 255, 0.1)',
    text: '下载中',
    tagColor: 'processing'
  },
  completed: { 
    icon: <CheckCircleOutlined />, 
    color: '#52c41a', 
    bgColor: 'rgba(82, 196, 26, 0.1)',
    text: '已完成',
    tagColor: 'success'
  },
  failed: { 
    icon: <CloseCircleOutlined />, 
    color: '#ff4d4f', 
    bgColor: 'rgba(255, 77, 79, 0.1)',
    text: '失败',
    tagColor: 'error'
  },
}

export default function DownloadManager({ downloads, visible, onToggle, onRemove }) {
  if (downloads.length === 0) return null

  const activeCount = downloads.filter(
    (d) => d.status === 'pending' || d.status === 'downloading'
  ).length

  const completedCount = downloads.filter(d => d.status === 'completed').length

  return (
    <div className="download-manager">
      {/* 头部区域 - 渐变背景 */}
      <div 
        className="download-manager-header" 
        onClick={onToggle}
        style={{
          background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
          boxShadow: '0 2px 8px rgba(24, 144, 255, 0.3)',
        }}
      >
        <Space align="center">
          <CloudDownloadOutlined style={{ fontSize: 18 }} />
          <span style={{ fontWeight: 500 }}>下载管理</span>
          {activeCount > 0 && (
            <Badge
              count={activeCount}
              size="small"
              style={{ 
                backgroundColor: '#fff', 
                color: '#1890ff',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            />
          )}
          {completedCount > 0 && (
            <Tag color="#52c41a" style={{ marginLeft: 4, borderRadius: 10 }}>
              {completedCount} 已完成
            </Tag>
          )}
        </Space>
        <Button 
          type="text" 
          icon={visible ? <UpOutlined /> : <DownOutlined />}
          style={{ color: '#fff' }}
          size="small"
        />
      </div>

      {/* 下载列表区域 */}
      {visible && (
        <div className="download-manager-body">
          <List
            size="small"
            dataSource={downloads}
            renderItem={(item) => {
              const status = STATUS_MAP[item.status] || STATUS_MAP.pending
              const fileSize = item.file_size > 0 
                ? `${(item.file_size / 1024 / 1024).toFixed(1)} MB` 
                : ''
              
              return (
                <div 
                  className="download-item"
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #f0f0f0',
                    transition: 'all 0.2s ease',
                    background: status.bgColor,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                    {/* 文件图标 */}
                    <div 
                      style={{ 
                        width: 40, 
                        height: 40, 
                        borderRadius: 8,
                        background: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        flexShrink: 0
                      }}
                    >
                      <FileOutlined style={{ fontSize: 18, color: '#1890ff' }} />
                    </div>

                    {/* 文件信息 */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                        <Text 
                          ellipsis 
                          style={{ 
                            maxWidth: 180, 
                            fontSize: 13, 
                            fontWeight: 500,
                            color: '#333'
                          }}
                          title={item.title}
                        >
                          {item.title}
                        </Text>
                        <Tag 
                          color={status.tagColor} 
                          style={{ 
                            fontSize: 11, 
                            padding: '0 6px',
                            borderRadius: 4,
                            margin: 0
                          }}
                        >
                          {status.icon} {status.text}
                        </Tag>
                      </div>
                      
                      {/* 文件大小 */}
                      {fileSize && (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {fileSize}
                        </Text>
                      )}

                      {/* 进度条 */}
                      {item.status === 'downloading' && (
                        <Progress
                          percent={50}
                          size="small"
                          status="active"
                          strokeColor={{
                            '0%': '#1890ff',
                            '100%': '#096dd9',
                          }}
                          style={{ marginTop: 8, marginBottom: 0 }}
                        />
                      )}
                    </div>

                    {/* 操作按钮 */}
                    <Space size={4}>
                      {item.status === 'completed' && (
                        <Tooltip title="下载文件">
                          <Button
                            type="primary"
                            size="small"
                            icon={<DownloadOutlined />}
                            href={`/api/download/file/${item.id}`}
                            target="_blank"
                            style={{ borderRadius: 4 }}
                          />
                        </Tooltip>
                      )}
                      <Tooltip title="移除">
                        <Button
                          type="text"
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={() => onRemove(item.id)}
                          danger
                          style={{ borderRadius: 4 }}
                        />
                      </Tooltip>
                    </Space>
                  </div>
                </div>
              )
            }}
          />
          
          {/* 底部统计 */}
          {downloads.length > 0 && (
            <div 
              style={{ 
                padding: '8px 16px', 
                background: '#fafafa',
                borderTop: '1px solid #f0f0f0',
                fontSize: 12,
                color: '#999',
                textAlign: 'center'
              }}
            >
              共 {downloads.length} 个下载任务
            </div>
          )}
        </div>
      )}
    </div>
  )
}
