import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 如果是 blob 响应（如 PDF 下载），返回整个 response 对象
    if (response.config.responseType === 'blob') {
      return response
    }
    // 其他情况返回 response.data
    return response.data
  },
  error => {
    if (error.response) {
      if (error.response.status === 401) {
        removeToken()
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        // 对于 blob 响应，错误信息可能在 error.response.data 中（需要解析）
        if (error.config && error.config.responseType === 'blob') {
          // blob 错误需要读取为文本
          error.response.data.text().then(text => {
            try {
              const errorData = JSON.parse(text)
              ElMessage.error(errorData.detail || '请求失败')
            } catch {
              ElMessage.error('请求失败')
            }
          })
        } else {
          ElMessage.error(error.response.data.detail || '请求失败')
        }
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default service

