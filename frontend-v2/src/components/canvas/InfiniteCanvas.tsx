import { useCallback, useEffect, useRef } from 'react'
import { Tldraw, TLShape, TLShapeId, createShapeId, toRichText, TLHandle, unique } from 'tldraw'
import 'tldraw/tldraw.css'
import { useAppStore } from '@/stores/appStore'

interface WorkflowStage {
  id: string
  name: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  content?: string
}

interface InfiniteCanvasProps {
  mainNodeTitle: string
  workflowStages: WorkflowStage[]
}

export function InfiniteCanvas({ mainNodeTitle, workflowStages }: InfiniteCanvasProps) {
  const { setSelectedNode, setCanvasViewport, setEditorInstance } = useAppStore()
  const editorRef = useRef<any>(null)
  const nodesCreatedRef = useRef(false)

  const createMainNode = useCallback((editor: any) => {
    const mainNodeId = createShapeId('main-node')

    try {
      // 使用 editor.createShape 的正确API方式
      editor.createShape({
        id: mainNodeId,
        type: 'geo',
        x: 100,
        y: 100,
        props: {
          w: 300,
          h: 80,
          geo: 'rectangle',
          color: 'blue',
          fill: 'solid'
        }
      })

      // 创建文本标签
      const textNodeId = createShapeId('main-text')
      editor.createShape({
        id: textNodeId,
        type: 'text',
        x: 120,
        y: 130,
        props: {
          richText: toRichText(mainNodeTitle),
          size: 'm',
          color: 'black',
          autoSize: true,
          textAlign: 'middle'
        }
      })
    } catch (error) {
      console.error('Failed to create main node:', error)
    }

    return mainNodeId
  }, [mainNodeTitle])

  const createStageNodes = useCallback((editor: any) => {
    if (!workflowStages || workflowStages.length === 0) return

    const nodeIds: TLShapeId[] = []

    workflowStages.forEach((stage, index) => {
      const nodeId = createShapeId(`stage-${stage.id}`)

      try {
        // Determine node color based on status
        let color = 'grey'
        let fill = 'none'

        switch (stage.status) {
          case 'completed':
            color = 'green'
            fill = 'solid'
            break
          case 'in_progress':
            color = 'blue'
            fill = 'pattern'
            break
          case 'pending':
            color = 'grey'
            fill = 'none'
            break
        }

        // 创建阶段节点（几何形状）
        editor.createShape({
          id: nodeId,
          type: 'geo',
          x: 50 + (index * 350),
          y: 250,
          props: {
            w: 280,
            h: 120,
            geo: 'rectangle',
            color: color,
            fill: fill
          }
        })

        // 创建阶段节点的文本标签
        const textNodeId = createShapeId(`stage-text-${stage.id}`)
        editor.createShape({
          id: textNodeId,
          type: 'text',
          x: 60 + (index * 350),
          y: 280,
          props: {
            richText: toRichText(`${stage.title}\n\n${stage.description}`),
            size: 's',
            color: 'black',
            w: 260,
            autoSize: false,
            textAlign: 'start'
          }
        })
        nodeIds.push(nodeId)

        // Create connection line from main node to this stage
        if (index === 0) {
          const lineId = createShapeId(`line-main-${stage.id}`)
          const startPointId = createShapeId('start-point')
          const endPointId = createShapeId('end-point')

          editor.createShape({
            id: lineId,
            type: 'line',
            x: 0,
            y: 0,
            props: {
              points: {
                [startPointId]: {
                  id: startPointId,
                  index: 'a1' as any,
                  x: 250,
                  y: 180
                },
                [endPointId]: {
                  id: endPointId,
                  index: 'a2' as any,
                  x: 50 + (index * 350) + 140,
                  y: 250
                }
              },
              color: 'black'
            }
          })
        }

        // Create connection lines between stages
        if (index > 0) {
          const lineId = createShapeId(`line-${workflowStages[index - 1].id}-${stage.id}`)
          const startPointId = createShapeId(`stage-line-start-${index}`)
          const endPointId = createShapeId(`stage-line-end-${index}`)

          editor.createShape({
            id: lineId,
            type: 'line',
            x: 0,
            y: 0,
            props: {
              points: {
                [startPointId]: {
                  id: startPointId,
                  index: 'a1' as any,
                  x: 50 + ((index - 1) * 350) + 280,
                  y: 310
                },
                [endPointId]: {
                  id: endPointId,
                  index: 'a2' as any,
                  x: 50 + (index * 350),
                  y: 310
                }
              },
              color: 'black'
            }
          })
        }

      } catch (error) {
        console.error(`Failed to create stage node ${stage.id}:`, error)
      }
    })

    return nodeIds
  }, [workflowStages])

  const updateStageNodes = useCallback((editor: any) => {
    if (!workflowStages || workflowStages.length === 0) return

    workflowStages.forEach((stage, index) => {
      const nodeId = createShapeId(`stage-${stage.id}`)

      try {
        const existingShape = editor.getShape(nodeId)
        if (existingShape) {
          // Determine node color based on status
          let color = 'grey'
          let fill = 'none'

          switch (stage.status) {
            case 'completed':
              color = 'green'
              fill = 'solid'
              break
            case 'in_progress':
              color = 'blue'
              fill = 'pattern'
              break
            case 'pending':
              color = 'grey'
              fill = 'none'
              break
          }

          // Update the shape with new status
          editor.updateShape({
            id: nodeId,
            type: 'geo',
            props: {
              ...existingShape.props,
              color: color,
              fill: fill
            }
          })

          // Update corresponding text shape
          const textNodeId = createShapeId(`stage-text-${stage.id}`)
          const existingTextShape = editor.getShape(textNodeId)
          if (existingTextShape) {
            const newText = stage.content ?
              `${stage.title}\n\n✅ 内容已生成\n点击查看详情` :
              `${stage.title}\n\n${stage.description}`

            editor.updateShape({
              id: textNodeId,
              type: 'text',
              props: {
                ...existingTextShape.props,
                richText: toRichText(newText)
              }
            })
          }
        }
      } catch (error) {
        console.error(`Failed to update stage node ${stage.id}:`, error)
      }
    })
  }, [workflowStages])

  const handleMount = useCallback((editor: unknown) => {
    editorRef.current = editor
    setEditorInstance(editor)

    // Create initial nodes
    setTimeout(() => {
      if (!nodesCreatedRef.current) {
        createMainNode(editor as any)
        createStageNodes(editor as any)
        nodesCreatedRef.current = true

        // Fit the canvas to show all nodes
        try {
          (editor as any).zoomToFit()
        } catch (error) {
          console.debug('Zoom to fit failed:', error)
        }
      }
    }, 500)

    // Event listeners for selection and camera changes
    let lastSelection: string[] = []
    let lastCamera = { x: 0, y: 0, z: 1 }

    const checkChanges = () => {
      try {
        // Check selection changes
        const currentSelection = (editor as any)?.getSelectedShapeIds ? (editor as any).getSelectedShapeIds() : []
        if (JSON.stringify(currentSelection) !== JSON.stringify(lastSelection)) {
          lastSelection = currentSelection
          if (currentSelection.length === 1) {
            setSelectedNode(currentSelection[0])
          } else {
            setSelectedNode(null)
          }
        }

        // Check camera changes
        const camera = (editor as any)?.getCamera ? (editor as any).getCamera() : { x: 0, y: 0, z: 1 }
        if (camera.x !== lastCamera.x || camera.y !== lastCamera.y || camera.z !== lastCamera.z) {
          lastCamera = camera
          setCanvasViewport({
            x: camera.x,
            y: camera.y,
            zoom: camera.z
          })
        }
      } catch (error) {
        console.debug('Canvas API call failed:', error)
      }
    }

    const interval = setInterval(checkChanges, 100)
    return () => clearInterval(interval)
  }, [setSelectedNode, setCanvasViewport, setEditorInstance, createMainNode, createStageNodes])

  // Update nodes when workflow stages change
  useEffect(() => {
    if (editorRef.current && nodesCreatedRef.current) {
      updateStageNodes(editorRef.current)
    }
  }, [workflowStages, updateStageNodes])

  return (
    <div className="canvas-container h-full">
      <Tldraw
        onMount={handleMount}
        persistenceKey="pbl-course-canvas"
      />
    </div>
  )
}