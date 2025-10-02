import { useState, useEffect, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { apiService } from '@/services/api'
import type { Stage1Output, Stage2Output, Stage3Output } from '@/services/api'
import { InfiniteCanvas } from '@/components/canvas/InfiniteCanvas'
import { WorkflowSidebar } from '@/components/workflow/WorkflowSidebar'

interface CourseInfo {
  courseType: string
  topic: string
  description: string
  studentAge: number
  studentCount: number
  duration: string
  specialRequirements: string
}

type StageStatus = 'pending' | 'generating' | 'completed' | 'editing' | 'error'

export function CourseDesignPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null)
  const [currentStage, setCurrentStage] = useState<1 | 2 | 3 | 'complete'>(1)

  // Stage data and status
  const [stage1Status, setStage1Status] = useState<StageStatus>('pending')
  const [stage1Data, setStage1Data] = useState<Stage1Output | null>(null)
  const [stage1EditableContent, setStage1EditableContent] = useState('')

  const [stage2Status, setStage2Status] = useState<StageStatus>('pending')
  const [stage2Data, setStage2Data] = useState<Stage2Output | null>(null)
  const [stage2EditableContent, setStage2EditableContent] = useState('')

  const [stage3Status, setStage3Status] = useState<StageStatus>('pending')
  const [stage3Data, setStage3Data] = useState<Stage3Output | null>(null)
  const [stage3EditableContent, setStage3EditableContent] = useState('')

  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    const dataParam = searchParams.get('data')
    if (dataParam) {
      try {
        const decodedData = JSON.parse(decodeURIComponent(dataParam))
        setCourseInfo(decodedData)
      } catch (error) {
        console.error('Failed to parse course data:', error)
        navigate('/create')
      }
    } else {
      navigate('/create')
    }
  }, [searchParams, navigate])

  // ========== Stage 1: Project Foundation ==========
  const startStage1 = async () => {
    if (!courseInfo) return

    setStage1Status('generating')
    setErrorMessage(null)

    try {
      const response = await apiService.generateStage1({
        course_topic: courseInfo.topic,
        course_overview: courseInfo.description,
        age_group: `${courseInfo.studentAge}岁`,
        duration: courseInfo.duration,
        ai_tools: courseInfo.courseType === 'stem' ? 'Claude Code, 豆包, 秒哈' : '相关创作工具'
      })

      if (response.success && response.data) {
        setStage1Data(response.data)
        setStage1EditableContent(response.data.raw_content)
        setStage1Status('completed')
      } else {
        setStage1Status('error')
        setErrorMessage(response.error || '阶段1生成失败')
      }
    } catch (error) {
      setStage1Status('error')
      setErrorMessage(error instanceof Error ? error.message : '阶段1生成异常')
    }
  }

  const editStage1 = () => {
    setStage1Status('editing')
  }

  const confirmStage1 = () => {
    setStage1Status('completed')
    setCurrentStage(2)
  }

  // ========== Stage 2: Assessment Framework ==========
  const startStage2 = async () => {
    if (!courseInfo || !stage1Data) return

    setStage2Status('generating')
    setErrorMessage(null)

    try {
      // Extract edited values from stage1
      const drivingQuestion = stage1Data.driving_question
      const projectDefinition = stage1Data.project_definition
      const finalDeliverable = stage1Data.final_deliverable

      const response = await apiService.generateStage2({
        driving_question: drivingQuestion,
        project_definition: projectDefinition,
        final_deliverable: finalDeliverable,
        course_topic: courseInfo.topic,
        age_group: `${courseInfo.studentAge}岁`,
        duration: courseInfo.duration
      })

      if (response.success && response.data) {
        setStage2Data(response.data)
        setStage2EditableContent(response.data.raw_content)
        setStage2Status('completed')
      } else {
        setStage2Status('error')
        setErrorMessage(response.error || '阶段2生成失败')
      }
    } catch (error) {
      setStage2Status('error')
      setErrorMessage(error instanceof Error ? error.message : '阶段2生成异常')
    }
  }

  const editStage2 = () => {
    setStage2Status('editing')
  }

  const confirmStage2 = () => {
    setStage2Status('completed')
    setCurrentStage(3)
  }

  // ========== Stage 3: Learning Blueprint ==========
  const startStage3 = async () => {
    if (!courseInfo || !stage1Data || !stage2Data) return

    setStage3Status('generating')
    setErrorMessage(null)

    try {
      const response = await apiService.generateStage3({
        driving_question: stage1Data.driving_question,
        project_definition: stage1Data.project_definition,
        final_deliverable: stage1Data.final_deliverable,
        rubric_markdown: stage2EditableContent, // Use edited content
        evaluation_criteria: stage2Data.evaluation_criteria,
        course_topic: courseInfo.topic,
        age_group: `${courseInfo.studentAge}岁`,
        duration: courseInfo.duration,
        ai_tools: courseInfo.courseType === 'stem' ? 'Claude Code, 豆包, 秒哈' : '相关创作工具'
      })

      if (response.success && response.data) {
        setStage3Data(response.data)
        setStage3EditableContent(response.data.raw_content)
        setStage3Status('completed')
        setCurrentStage('complete')
      } else {
        setStage3Status('error')
        setErrorMessage(response.error || '阶段3生成失败')
      }
    } catch (error) {
      setStage3Status('error')
      setErrorMessage(error instanceof Error ? error.message : '阶段3生成异常')
    }
  }

  const editStage3 = () => {
    setStage3Status('editing')
  }

  // ========== Export ==========
  const exportCourse = () => {
    if (!courseInfo) return

    const fullContent = `# ${courseInfo.topic} - 完整PBL课程设计方案

生成时间: ${new Date().toLocaleString('zh-CN')}

---

## 阶段1: 项目基础定义

${stage1EditableContent}

---

## 阶段2: 评估框架设计

${stage2EditableContent}

---

## 阶段3: 学习蓝图

${stage3EditableContent}

---

**课程基本信息**
- 课程类型: ${courseInfo.courseType}
- 学生年龄: ${courseInfo.studentAge}岁
- 学生人数: ${courseInfo.studentCount}人
- 课程时长: ${courseInfo.duration}
- 特殊要求: ${courseInfo.specialRequirements || '无'}
`

    const blob = new Blob([fullContent], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${courseInfo.topic}-PBL课程设计-${new Date().getTime()}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  // ========== Map state to WorkflowStages format ==========
  const workflowStages = useMemo(() => [
    {
      id: 'stage1',
      name: '项目基础',
      title: '阶段1: 项目基础定义',
      description: '确定项目范围、目标和基本框架',
      status: stage1Status === 'completed' ? 'completed' as const :
              stage1Status === 'generating' || stage1Status === 'editing' ? 'in_progress' as const :
              'pending' as const,
      content: stage1EditableContent
    },
    {
      id: 'stage2',
      name: '评估框架',
      title: '阶段2: 评估框架设计',
      description: '设计评估标准和量规',
      status: stage2Status === 'completed' ? 'completed' as const :
              stage2Status === 'generating' || stage2Status === 'editing' ? 'in_progress' as const :
              'pending' as const,
      content: stage2EditableContent
    },
    {
      id: 'stage3',
      name: '学习蓝图',
      title: '阶段3: 学习蓝图生成',
      description: '生成详细的教学计划',
      status: stage3Status === 'completed' ? 'completed' as const :
              stage3Status === 'generating' || stage3Status === 'editing' ? 'in_progress' as const :
              'pending' as const,
      content: stage3EditableContent
    }
  ], [stage1Status, stage1EditableContent, stage2Status, stage2EditableContent, stage3Status, stage3EditableContent])

  // ========== Render ==========
  if (!courseInfo) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载课程信息...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
            <h1 className="text-xl font-semibold text-gray-900">
              课程设计工作台 - {courseInfo.topic}
            </h1>
          </div>
          <div className="text-sm text-gray-600">
            {currentStage === 'complete' ? '已完成' : `阶段 ${currentStage}`}
          </div>
        </div>
      </header>

      {/* Main Layout: Canvas (left) + Workflow Sidebar (right) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Infinite Canvas */}
        <div className="flex-1 relative">
          <InfiniteCanvas
            mainNodeTitle={`${courseInfo.topic} PBL课程`}
            workflowStages={workflowStages}
          />
        </div>

        {/* Right: Workflow Sidebar */}
        <WorkflowSidebar
          stages={[
            {
              number: 1,
              name: '项目基础定义',
              status: stage1Status,
              content: stage1EditableContent,
              onStart: startStage1,
              onEdit: editStage1,
              onConfirm: confirmStage1,
              onContentChange: setStage1EditableContent,
              errorMessage: stage1Status === 'error' ? errorMessage || undefined : undefined
            },
            {
              number: 2,
              name: '评估框架设计',
              status: stage2Status,
              content: stage2EditableContent,
              onStart: startStage2,
              onEdit: editStage2,
              onConfirm: confirmStage2,
              onContentChange: setStage2EditableContent,
              errorMessage: stage2Status === 'error' ? errorMessage || undefined : undefined
            },
            {
              number: 3,
              name: '学习蓝图生成',
              status: stage3Status,
              content: stage3EditableContent,
              onStart: startStage3,
              onEdit: editStage3,
              onConfirm: () => {
                setStage3Status('completed')
                setCurrentStage('complete')
              },
              onContentChange: setStage3EditableContent,
              errorMessage: stage3Status === 'error' ? errorMessage || undefined : undefined
            }
          ]}
          currentStage={currentStage}
          onExport={exportCourse}
          courseTitle={courseInfo.topic}
        />
      </div>
    </div>
  )
}
