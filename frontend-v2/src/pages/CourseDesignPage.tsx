import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle, AlertCircle, Play } from 'lucide-react'
import { InfiniteCanvas } from '@/components/canvas/InfiniteCanvas'
import { ChatSidebar } from '@/components/chat/ChatSidebar'
import { useAppStore } from '@/stores/appStore'

interface CourseInfo {
  courseType: string
  topic: string
  description: string
  studentAge: number
  studentCount: number
  duration: string
  specialRequirements: string
}

interface WorkflowStage {
  id: string
  name: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  content?: string
}

export function CourseDesignPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isChatOpen, setChatOpen } = useAppStore()

  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null)
  const [workflowStages, setWorkflowStages] = useState<WorkflowStage[]>([
    {
      id: 'stage1',
      name: '项目基础定义',
      title: '项目基础定义',
      description: '确定项目范围、目标和基本框架',
      status: 'pending'
    },
    {
      id: 'stage2',
      name: '评估框架',
      title: '评估框架设计',
      description: '建立评估标准和方法',
      status: 'pending'
    },
    {
      id: 'stage3',
      name: '学习蓝图',
      title: '学习蓝图生成',
      description: '制定详细的学习活动和时间安排',
      status: 'pending'
    }
  ])

  const [currentStageIndex, setCurrentStageIndex] = useState(0)
  const [isWorkflowStarted, setIsWorkflowStarted] = useState(false)
  const [showStageConfirmation, setShowStageConfirmation] = useState(false)

  useEffect(() => {
    // 从URL参数中获取课程信息
    const dataParam = searchParams.get('data')
    if (dataParam) {
      try {
        const decodedData = JSON.parse(decodeURIComponent(dataParam))
        setCourseInfo(decodedData)
      } catch (error) {
        console.error('Failed to parse course data:', error)
        // 如果解析失败，返回创建页面
        navigate('/create')
      }
    } else {
      // 如果没有课程数据，返回创建页面
      navigate('/create')
    }
  }, [searchParams, navigate])

  const startWorkflow = async () => {
    if (!courseInfo) return

    setIsWorkflowStarted(true)
    setChatOpen(true)

    // 开始第一阶段
    await startStage(0)
  }

  const startStage = async (stageIndex: number) => {
    if (stageIndex >= workflowStages.length) return

    setCurrentStageIndex(stageIndex)

    // 更新阶段状态
    setWorkflowStages(prev =>
      prev.map((stage, index) => ({
        ...stage,
        status: index === stageIndex ? 'in_progress' :
                index < stageIndex ? 'completed' : 'pending'
      }))
    )

    // 模拟AI生成阶段内容
    setTimeout(() => {
      generateStageContent(stageIndex)
    }, 2000)
  }

  const generateStageContent = (stageIndex: number) => {
    if (!courseInfo) return

    const stage = workflowStages[stageIndex]
    let generatedContent = ''

    switch (stageIndex) {
      case 0: // 项目基础定义
        generatedContent = `# ${courseInfo.topic} - 项目基础定义

## 项目概述
**课程类型**: ${courseInfo.courseType}
**目标学生**: ${courseInfo.studentAge}岁学生，约${courseInfo.studentCount}人
**项目周期**: ${courseInfo.duration}

## 驱动性问题
基于"${courseInfo.topic}"主题的核心问题探究

## 学习目标
1. 知识目标：掌握${courseInfo.topic}相关的核心概念
2. 技能目标：培养项目管理和团队协作能力
3. 素养目标：形成可持续发展意识和创新思维

## 项目成果
学生将完成一个关于${courseInfo.topic}的实际项目作品

${courseInfo.specialRequirements ? `## 特殊要求\n${courseInfo.specialRequirements}` : ''}`
        break

      case 1: // 评估框架
        generatedContent = `# ${courseInfo.topic} - 评估框架设计

## 评估维度
1. **过程评估** (40%)
   - 项目计划制定
   - 团队协作表现
   - 学习反思记录

2. **成果评估** (40%)
   - 项目作品质量
   - 创新性和实用性
   - 问题解决能力

3. **展示评估** (20%)
   - 成果展示效果
   - 沟通表达能力
   - 回答问题水平

## 评估方法
- 同伴互评
- 自我评价
- 教师观察
- 专家点评

## 评估时间节点
- 项目启动期评估
- 中期进展评估
- 最终成果评估`
        break

      case 2: // 学习蓝图
        generatedContent = `# ${courseInfo.topic} - 学习蓝图

## 课程实施计划 (${courseInfo.duration})

### 第1周：项目启动
- 问题提出与分析
- 团队组建
- 初步调研

### 第2-3周：深入探究
- 资料收集与整理
- 实地调研或实验
- 方案设计

### 第4周：项目实施
- 原型制作或方案执行
- 测试与改进
- 成果完善

### 最后周：展示评估
- 成果展示准备
- 项目答辩
- 反思总结

## 资源需求
- 学习材料：相关书籍、视频资源
- 技术工具：${courseInfo.courseType === 'STEM' ? '实验设备、计算机软件' : '创作工具、展示设备'}
- 外部资源：专家指导、实践基地

## 教师指导要点
1. 问题引导而非直接给答案
2. 及时反馈学生进展
3. 促进团队协作
4. 关注个体差异`
        break
    }

    // 更新阶段内容
    setWorkflowStages(prev =>
      prev.map((s, index) =>
        index === stageIndex
          ? { ...s, content: generatedContent, status: 'completed' }
          : s
      )
    )

    // 显示确认对话框
    setShowStageConfirmation(true)
  }

  const confirmStage = () => {
    setShowStageConfirmation(false)

    if (currentStageIndex < workflowStages.length - 1) {
      // 进入下一阶段
      setTimeout(() => {
        startStage(currentStageIndex + 1)
      }, 500)
    } else {
      // 所有阶段完成
      console.log('Course creation completed!')
    }
  }

  const modifyStage = () => {
    setShowStageConfirmation(false)
    // 这里可以打开编辑界面
    console.log('Modify stage:', currentStageIndex)
  }

  const getMainNodeTitle = () => {
    return courseInfo ? `${courseInfo.topic} PBL课程研发任务` : '课程设计任务'
  }

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

          {/* Workflow Progress */}
          <div className="flex items-center space-x-4">
            {workflowStages.map((stage, index) => (
              <div key={stage.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                  stage.status === 'completed' ? 'bg-green-100 text-green-800' :
                  stage.status === 'in_progress' ? 'bg-indigo-100 text-indigo-800' :
                  'bg-gray-100 text-gray-500'
                }`}>
                  {stage.status === 'completed' ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span className="ml-2 text-sm text-gray-600">{stage.name}</span>
                {index < workflowStages.length - 1 && (
                  <div className="mx-3 w-8 h-px bg-gray-300" />
                )}
              </div>
            ))}
          </div>

          {!isWorkflowStarted && (
            <button
              onClick={startWorkflow}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
            >
              <Play className="w-4 h-4" />
              <span>开始工作流</span>
            </button>
          )}
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Canvas Area */}
        <div className="flex-1 relative">
          <InfiniteCanvas
            mainNodeTitle={getMainNodeTitle()}
            workflowStages={workflowStages}
          />
        </div>

        {/* Chat Sidebar */}
        {isChatOpen && (
          <div className="w-96 border-l border-gray-200">
            <ChatSidebar />
          </div>
        )}
      </div>

      {/* Stage Confirmation Modal */}
      {showStageConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                {workflowStages[currentStageIndex]?.title} 已完成
              </h3>
            </div>

            <div className="mb-6">
              <p className="text-gray-600 mb-4">
                AI已为您生成了本阶段的内容。请查看以下内容是否满足您的需求：
              </p>

              <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                  {workflowStages[currentStageIndex]?.content}
                </pre>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={modifyStage}
                className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
              >
                修改内容
              </button>
              <button
                onClick={confirmStage}
                className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                {currentStageIndex < workflowStages.length - 1 ? '确认并继续下一阶段' : '确认完成'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}