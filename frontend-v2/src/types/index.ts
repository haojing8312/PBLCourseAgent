// Core types for the PBL Course Agent application

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export interface Course {
  id: string
  title: string
  description: string
  subject: string
  targetAudience: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimatedDuration: number // in hours
  createdAt: Date
  updatedAt: Date
  status: 'draft' | 'in_progress' | 'completed' | 'published'
}

export interface Task {
  id: string
  title: string
  description: string
  type: 'research' | 'design' | 'implementation' | 'presentation' | 'reflection'
  estimatedTime: number // in minutes
  resources: Resource[]
  deliverables: Deliverable[]
  assessmentCriteria: AssessmentCriterion[]
  dependencies: string[] // task IDs
  position: { x: number; y: number } // Canvas position
  status: 'pending' | 'in_progress' | 'completed'
  courseId: string
}

export interface Resource {
  id: string
  title: string
  type: 'link' | 'document' | 'video' | 'tool' | 'reference'
  url?: string
  content?: string
  description?: string
}

export interface Deliverable {
  id: string
  title: string
  description: string
  format: 'document' | 'presentation' | 'prototype' | 'code' | 'report'
  requirements: string[]
}

export interface AssessmentCriterion {
  id: string
  name: string
  description: string
  weight: number // percentage
  rubric: RubricLevel[]
}

export interface RubricLevel {
  level: 'excellent' | 'good' | 'satisfactory' | 'needs_improvement'
  score: number
  description: string
}

// Canvas-related types
export interface CanvasNode {
  id: string
  type: 'task' | 'milestone' | 'resource' | 'note'
  position: { x: number; y: number }
  size: { width: number; height: number }
  data: TaskNode | MilestoneNode | ResourceNode | NoteNode
}

export interface TaskNode {
  taskId: string
  task: Task
  color: string
}

export interface MilestoneNode {
  title: string
  description: string
  dueDate: Date
  tasks: string[] // task IDs
  color: string
}

export interface ResourceNode {
  resource: Resource
  color: string
}

export interface NoteNode {
  content: string
  color: string
  author: string
}

export interface CanvasConnection {
  id: string
  source: string // node ID
  target: string // node ID
  type: 'dependency' | 'flow' | 'reference'
  label?: string
}

// AI Agent related types
export interface AgentMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agentType?: 'foundation' | 'assessment' | 'blueprint'
  metadata?: Record<string, unknown>
}

export interface WorkflowStep {
  id: string
  name: string
  description: string
  agentType: 'foundation' | 'assessment' | 'blueprint'
  status: 'pending' | 'running' | 'completed' | 'error'
  input?: Record<string, unknown>
  output?: Record<string, unknown>
  progress?: number
}

// UI State types
export interface AppState {
  currentCourse: Course | null
  selectedNode: string | null
  canvasViewport: { x: number; y: number; zoom: number }
  sidebarOpen: boolean
  chatOpen: boolean
  currentWorkflow: WorkflowStep[] | null
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// Export types
export interface ExportOptions {
  format: 'pdf' | 'docx' | 'json' | 'png'
  includeCanvas: boolean
  includeResources: boolean
  includeAssessment: boolean
  templateStyle?: 'modern' | 'classic' | 'minimal'
}

export interface ExportResult {
  success: boolean
  downloadUrl?: string
  error?: string
}