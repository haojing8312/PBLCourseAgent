// API service for backend communication

interface ProjectInput {
  course_topic: string
  course_overview: string
  age_group: string
  duration: string
  ai_tools: string
}

interface ApiResponse<T = unknown> {
  success: boolean
  message: string
  data?: T
  error?: string
  timestamp: string
}

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}/api/v1${endpoint}`

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    }

    const config = { ...defaultOptions, ...options }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.message || 'API request failed')
      }

      return data as ApiResponse<T>
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Health check endpoint
  async healthCheck(): Promise<ApiResponse> {
    return this.request('/health')
  }

  // Status endpoint
  async getStatus(): Promise<ApiResponse> {
    return this.request('/status')
  }

  // Generate course endpoint
  async generateCourse(input: ProjectInput): Promise<ApiResponse> {
    return this.request('/generate', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }
}

// Export singleton instance
export const apiService = new ApiService()
export type { ProjectInput, ApiResponse }