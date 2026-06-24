/**
 * API client for the FastAPI backend.
 * Centralized here so the base URL only needs to change in one place
 * (e.g. when moving from localhost to a deployed backend URL).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

/**
 * Upload a resume PDF and get ranked job matches.
 * @param {File} file - The PDF file object
 * @param {number} topK - Number of results to return
 */
export async function matchResume(file, topK = 10) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('top_k', String(topK))

  let response
  try {
    response = await fetch(`${API_BASE}/match`, {
      method: 'POST',
      body: formData,
    })
  } catch (networkErr) {
    throw new ApiError(
      "Can't reach the matching server. Is the backend running on port 8000?",
      0
    )
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message = typeof detail === 'string'
      ? detail
      : 'Something went wrong while matching your resume.'
    throw new ApiError(message, response.status)
  }

  return response.json()
}

/**
 * Check backend health and index status.
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) return null
    return response.json()
  } catch {
    return null
  }
}
