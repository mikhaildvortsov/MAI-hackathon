const getApiBase = () => {
  const meta = document.querySelector('meta[name="bizmail-api-base"]')
  if (meta?.content) return meta.content.replace(/\/$/, '')
  return 'http://localhost:8001'
}

export const analyzeEmail = async (subject, body, companyContext) => {
  const apiBase = getApiBase()
  const response = await fetch(`${apiBase}/api/emails/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_subject: subject,
      source_body: body,
      company_context: companyContext,
    }),
  })

  if (!response.ok) {
    throw new Error(`Ошибка анализа: HTTP ${response.status}`)
  }

  return response.json()
}

export const generateEmail = async (requestData) => {
  const apiBase = getApiBase()
  const response = await fetch(`${apiBase}/api/emails/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  })

  if (!response.ok) {
    let err = `HTTP ${response.status}`
    try {
      const payload = await response.json()
      if (payload.detail) {
        err = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)
      } else if (payload.message) {
        err = payload.message
      }
    } catch {}
    throw new Error(err)
  }

  return response.json()
}

