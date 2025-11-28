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
    const apiBase = getApiBase()
    setApiStatus(`Проверяем соединение с API (${apiBase})...`)
    try {
      const res = await fetch(`${apiBase}/health`)
      if (!res.ok) throw new Error(`Health check failed with ${res.status}`)
      setApiStatus(`✓ Бэкенд подключен (${apiBase})`)
    } catch (e) {
      setApiStatus(`✗ Нет связи с сервером ${apiBase}`)
    }
  }

  const getApiBase = () => {
    const meta = document.querySelector('meta[name="bizmail-api-base"]')
    if (meta?.content) return meta.content.replace(/\/$/, '')
    if (window.location.origin && window.location.origin.startsWith('http')) {
      return window.location.origin.replace(/\/$/, '')
    }
    return 'http://localhost:8001'
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

