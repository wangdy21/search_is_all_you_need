import axios from 'axios'
import { message } from 'antd'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 429) {
        message.error('请求过于频繁，请稍后再试')
      } else if (status >= 500) {
        message.error(data?.error || '服务器内部错误')
      } else if (status === 400) {
        message.warning(data?.error || '请求参数错误')
      }
    } else if (error.code === 'ECONNABORTED') {
      message.error('请求超时，该操作可能需要较长时间，请重试')
    } else {
      message.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default api
