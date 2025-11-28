import { useState, useEffect } from 'react'
import Homepage from './components/Homepage'
import Generator from './components/Generator'
import './styles/App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('homepage')
  const [apiStatus, setApiStatus] = useState('Проверяем соединение...')

  useEffect(() => {
    verifyBackend()
  }, [])

  const verifyBackend = async () => {
    setApiStatus('Проверяем соединение с API...')
    try {
      const apiBase = await getApiBase()
      const res = await fetch(`${apiBase}/health`)
      if (!res.ok) throw new Error(`Health check failed with ${res.status}`)
      setApiStatus(`✓ Бэкенд подключен (${apiBase})`)
    } catch (e) {
      setApiStatus(`✗ Нет связи с сервером. Проверьте порты 8000-8009`)
    }
  }

  const getApiBase = async () => {
    // Проверяем мета-тег
    const meta = document.querySelector('meta[name="bizmail-api-base"]')
    if (meta?.content) {
      const base = meta.content.replace(/\/$/, '')
      if (await checkBackendAvailable(base)) {
        return base
      }
    }
    
    // Пробуем найти бэкенд на портах 8000-8009
    const ports = [8001, 8000, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009]
    for (const port of ports) {
      const base = `http://localhost:${port}`
      if (await checkBackendAvailable(base)) {
        return base
      }
    }
    
    // Fallback на стандартный порт
    return 'http://localhost:8001'
  }

  const checkBackendAvailable = async (baseUrl) => {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 1000) // 1 секунда таймаут
      const res = await fetch(`${baseUrl}/health`, {
        signal: controller.signal,
        method: 'GET',
      })
      clearTimeout(timeoutId)
      return res.ok
    } catch {
      return false
    }
  }

  return (
    <div className="app">
      {currentPage === 'homepage' ? (
        <Homepage onStart={() => setCurrentPage('generator')} apiStatus={apiStatus} />
      ) : (
        <Generator onBack={() => setCurrentPage('homepage')} apiStatus={apiStatus} />
      )}
    </div>
  )
}

export default App

