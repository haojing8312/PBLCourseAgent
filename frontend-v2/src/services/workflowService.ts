import { createShapeId } from 'tldraw'
import { apiService } from './api'

export interface WorkflowNode {
  id: string
  title: string
  type: 'input' | 'agent' | 'output'
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  position: { x: number; y: number }
  props?: any
}

export class WorkflowService {
  private editorInstance: any = null

  setEditor(editor: any) {
    this.editorInstance = editor
  }

  /**
   * Initialize a default PBL course generation workflow on the canvas
   */
  async initializePBLWorkflow(): Promise<WorkflowNode[]> {
    if (!this.editorInstance) {
      throw new Error('Editor not initialized')
    }

    // Clear existing shapes
    try {
      const allShapes = (this.editorInstance as any).getCurrentPageShapes?.() || []
      const shapeIds = allShapes.map((shape: any) => shape.id)
      if (shapeIds.length > 0) {
        (this.editorInstance as any).deleteShapes?.(shapeIds)
      }
    } catch (error) {
      console.warn('Failed to clear existing shapes:', error)
    }

    // Define the PBL workflow nodes
    const workflowNodes: WorkflowNode[] = [
      {
        id: 'input-node',
        title: 'Course Input',
        type: 'input',
        status: 'pending',
        position: { x: 100, y: 200 },
        props: {
          description: 'Enter course topic, overview, age group, duration, and AI tools'
        }
      },
      {
        id: 'agent1-node',
        title: 'Project Foundation',
        type: 'agent',
        status: 'pending',
        position: { x: 400, y: 200 },
        props: {
          agent: 'project_foundation_agent',
          description: 'Generate driving question and project definition'
        }
      },
      {
        id: 'agent2-node',
        title: 'Assessment Framework',
        type: 'agent',
        status: 'pending',
        position: { x: 700, y: 200 },
        props: {
          agent: 'assessment_framework_agent',
          description: 'Create evaluation rubrics and assessment criteria'
        }
      },
      {
        id: 'agent3-node',
        title: 'Learning Blueprint',
        type: 'agent',
        status: 'pending',
        position: { x: 1000, y: 200 },
        props: {
          agent: 'learning_blueprint_agent',
          description: 'Generate day-by-day learning plan and activities'
        }
      },
      {
        id: 'output-node',
        title: 'Complete Course',
        type: 'output',
        status: 'pending',
        position: { x: 1300, y: 200 },
        props: {
          description: 'Export and download complete PBL course package'
        }
      }
    ]

    // Create shapes for each workflow node
    for (const node of workflowNodes) {
      await this.createWorkflowNodeShape(node)
    }

    // TODO: Create connections between nodes (simplified for MVP)
    // await this.createWorkflowConnections(workflowNodes)

    // Fit the canvas to show all nodes
    try {
      (this.editorInstance as any).zoomToFit?.()
    } catch (error) {
      console.warn('Failed to zoom to fit:', error)
    }

    return workflowNodes
  }

  /**
   * Create a visual shape for a workflow node
   */
  private async createWorkflowNodeShape(node: WorkflowNode): Promise<void> {
    if (!this.editorInstance) return

    // Color scheme based on node type
    const colors = {
      input: 'green',
      agent: 'blue',
      output: 'orange'
    }

    // Status indicators (unused in this simple implementation)

    try {
      (this.editorInstance as any).createShape?.({
        id: node.id,
        type: 'geo',
        x: node.position.x,
        y: node.position.y,
        props: {
          geo: 'rectangle',
          w: 180,
          h: 100,
          fill: 'solid',
          color: colors[node.type],
          text: `${node.title}\n\n${node.props?.description || ''}`,
        },
      })
    } catch (error) {
      console.warn(`Failed to create shape for node ${node.id}:`, error)
    }
  }


  /**
   * Update the status of a workflow node
   */
  async updateNodeStatus(nodeId: string, status: WorkflowNode['status']): Promise<void> {
    if (!this.editorInstance) return

    const statusColors: Record<WorkflowNode['status'], string> = {
      pending: 'light-blue',
      in_progress: 'yellow',
      completed: 'green',
      error: 'red'
    }

    try {
      const shape = (this.editorInstance as any).getShape?.(nodeId)
      if (shape) {
        (this.editorInstance as any).updateShape?.({
          id: nodeId,
          type: 'geo',
          props: {
            ...shape.props,
            color: statusColors[status]
          }
        })
      }
    } catch (error) {
      console.warn(`Failed to update node ${nodeId} status:`, error)
    }
  }

  /**
   * Execute the PBL workflow by calling the backend API (without canvas dependency)
   *
   * Uses apiService for centralized API configuration and error handling.
   */
  async executePBLWorkflow(courseInput: {
    course_topic: string
    course_overview: string
    age_group: string
    duration: string
    ai_tools: string
  }): Promise<{
    success: boolean
    data?: any
    message?: string
    error?: string
  }> {
    try {
      // Update canvas nodes if editor is available (optional)
      if (this.editorInstance) {
        await this.updateNodeStatus('input-node', 'in_progress')
      }

      // Use apiService instead of direct fetch - eliminates hardcoded URL
      const result = await apiService.generateCourse(courseInput)

      if (result.success) {
        // Update canvas nodes if editor is available (optional)
        if (this.editorInstance) {
          await this.updateNodeStatus('input-node', 'completed')
          await this.updateNodeStatus('agent1-node', 'completed')
          await this.updateNodeStatus('agent2-node', 'completed')
          await this.updateNodeStatus('agent3-node', 'completed')
          await this.updateNodeStatus('output-node', 'completed')
        }

        return {
          success: true,
          data: result.data,
          message: result.message
        }
      } else {
        if (this.editorInstance) {
          await this.updateNodeStatus('input-node', 'error')
        }
        return {
          success: false,
          error: result.error || result.message || 'Workflow execution failed'
        }
      }
    } catch (error) {
      console.error('Workflow execution error:', error)
      if (this.editorInstance) {
        await this.updateNodeStatus('input-node', 'error')
      }
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }
}

// Export singleton instance
export const workflowService = new WorkflowService()