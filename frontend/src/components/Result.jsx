import React, { useState, useEffect } from 'react'
import './Result.css'

function Result({ result }) {
  const [subject, setSubject] = useState(result?.subject || '')
  const [body, setBody] = useState(result?.body || '')

  // Обновляем состояние при изменении result
  useEffect(() => {
    if (result) {
      setSubject(result.subject || '')
      setBody(result.body || '')
    }
  }, [result])

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    alert('Скопировано в буфер обмена!')
  }

  const handleCopyAll = () => {
    const fullText = `Тема: ${subject}\n\n${body}`
    navigator.clipboard.writeText(fullText)
    alert('Письмо скопировано в буфер обмена!')
  }

  if (!result) {
    return null
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <h3>Результат</h3>
        <div className="result-actions">
          <button className="btn-icon" onClick={handleCopyAll}>
            Копировать всё
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>Тема письма</label>
        <div
          className="result-field"
          contentEditable
          suppressContentEditableWarning
          onBlur={(e) => setSubject(e.target.textContent)}
        >
          {subject}
        </div>
        <button className="btn-icon" onClick={() => handleCopy(subject)}>
          Копировать тему
        </button>
      </div>

      <div className="form-group">
        <label>Текст письма</label>
        <div
          className="result-field"
          contentEditable
          suppressContentEditableWarning
          style={{ minHeight: '300px' }}
          onBlur={(e) => setBody(e.target.textContent)}
        >
          {body}
        </div>
        <button className="btn-icon" onClick={() => handleCopy(body)}>
          Копировать текст
        </button>
      </div>
    </div>
  )
}

export default Result

