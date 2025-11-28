import { useState } from 'react'
import './EmailForm.css'

function EmailForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    sender_first_name: '',
    sender_last_name: '',
    sender_position: '',
    source_subject: '',
    source_body: '',
    company_context: '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    const firstName = formData.sender_first_name.trim()
    const lastName = formData.sender_last_name.trim()
    const position = formData.sender_position.trim()

    if (!firstName || !lastName || !position) {
      alert('Заполните все данные отправителя (Имя, Фамилия, Должность)')
      return
    }

    const subject = formData.source_subject.trim()
    const body = formData.source_body.trim()

    if (!subject || !body) {
      alert('Заполните тему и текст входящего письма')
      return
    }

    onSubmit({
      sender_first_name: firstName,
      sender_last_name: lastName,
      sender_position: position,
      source_subject: subject,
      source_body: body,
      company_context: formData.company_context.trim() || 'ПАО Банк',
    })
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="email-form">
      <div className="sender-info">
        <h3 className="section-title">Данные отправителя</h3>
        <div className="sender-info-grid">
          <div className="form-group">
            <label htmlFor="sender_first_name">Имя *</label>
            <input
              type="text"
              id="sender_first_name"
              name="sender_first_name"
              value={formData.sender_first_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="sender_last_name">Фамилия *</label>
            <input
              type="text"
              id="sender_last_name"
              name="sender_last_name"
              value={formData.sender_last_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="sender_position">Должность *</label>
            <input
              type="text"
              id="sender_position"
              name="sender_position"
              value={formData.sender_position}
              onChange={handleChange}
              required
            />
          </div>
        </div>
      </div>

      <div className="two-column-grid">
        <div className="column-left">
          <div className="column-header">Входящее письмо</div>
          <div className="form-group">
            <label htmlFor="source_subject">Тема письма *</label>
            <input
              type="text"
              id="source_subject"
              name="source_subject"
              value={formData.source_subject}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="source_body">Текст письма *</label>
            <textarea
              id="source_body"
              name="source_body"
              value={formData.source_body}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="column-right">
          <div className="column-header">🏢 Контекст компании</div>
          <div className="form-group">
            <label htmlFor="company_context">Описание компании</label>
            <textarea
              id="company_context"
              name="company_context"
              value={formData.company_context}
              onChange={handleChange}
              placeholder="ПАО Банк"
            />
            <div className="hint">Используется для контекста в письмах</div>
          </div>
        </div>
      </div>

      <button type="submit" className="btn-analyze">
        🤖 Анализировать и сгенерировать ответ
      </button>
    </form>
  )
}

export default EmailForm

