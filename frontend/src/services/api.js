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
    const timeoutId = setTimeout(() => controller.abort(), 500) // 500ms таймаут для быстрой проверки
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

export const analyzeEmail = async (subject, body, companyContext) => {
  const apiBase = await getApiBase()
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

export const analyzeEmailDetailed = async (subject, body, companyContext) => {
  const API_BASE_URL = await getApiBase()
  const response = await fetch(`${API_BASE_URL}/api/emails/analyze-detailed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_subject: subject,
      source_body: body,
      company_context: companyContext,
    }),
  })

  if (!response.ok) {
    throw new Error(`Ошибка расширенного анализа: HTTP ${response.status}`)
  }

  return response.json()
}

export const generateEmail = async (requestData) => {
  const apiBase = await getApiBase()
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

