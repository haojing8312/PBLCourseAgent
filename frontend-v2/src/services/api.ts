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

// ========== Staged Generation Types ==========

interface Stage1Input {
  course_topic: string
  course_overview: string
  age_group: string
  duration: string
  ai_tools: string
}

interface Stage1Output {
  driving_question: string
  project_definition: string
  final_deliverable: string
  cover_page: string
  raw_content: string
  generation_time: number
}

interface Stage2Input {
  driving_question: string
  project_definition: string
  final_deliverable: string
  course_topic: string
  age_group: string
  duration: string
}

interface Stage2Output {
  rubric_markdown: string
  evaluation_criteria: string
  raw_content: string
  generation_time: number
}

interface Stage3Input {
  driving_question: string
  project_definition: string
  final_deliverable: string
  rubric_markdown: string
  evaluation_criteria: string
  course_topic: string
  age_group: string
  duration: string
  ai_tools: string
}

interface Stage3Output {
  day_by_day_plan: string
  activities_summary: string
  materials_list: string
  raw_content: string
  generation_time: number
}

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'
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

  // Generate course endpoint (legacy - one-shot generation)
  async generateCourse(input: ProjectInput): Promise<ApiResponse> {
    return this.request('/generate', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }

  // ========== Staged Generation Endpoints ==========

  // Stage 1: Generate project foundation
  async generateStage1(input: Stage1Input): Promise<ApiResponse<Stage1Output>> {
    return this.request<Stage1Output>('/generate/stage1', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }

  // Stage 2: Generate assessment framework based on Stage 1
  async generateStage2(input: Stage2Input): Promise<ApiResponse<Stage2Output>> {
    return this.request<Stage2Output>('/generate/stage2', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }

  // Stage 3: Generate learning blueprint based on Stage 1 + Stage 2
  async generateStage3(input: Stage3Input): Promise<ApiResponse<Stage3Output>> {
    return this.request<Stage3Output>('/generate/stage3', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  }
}

// Export singleton instance
export const apiService = new ApiService()
export type {
  ProjectInput,
  ApiResponse,
  Stage1Input,
  Stage1Output,
  Stage2Input,
  Stage2Output,
  Stage3Input,
  Stage3Output
}