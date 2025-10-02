import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Bot, User, CheckCircle } from 'lucide-react'

interface CourseInfo {
  courseType: string
  topic: string
  description: string
  studentAge: number
  studentCount: number
  duration: string
  specialRequirements: string
}

interface Message {
  id: string
  role: 'assistant' | 'user'
  content: string
  timestamp: Date
}

const COLLECTION_STEPS = [
  { key: 'courseType', label: '课程类型', completed: false },
  { key: 'topic', label: '课程主题', completed: false },
  { key: 'description', label: '课程描述', completed: false },
  { key: 'studentAge', label: '学生年龄', completed: false },
  { key: 'studentCount', label: '学生人数', completed: false },
  { key: 'duration', label: '课程周期', completed: false },
  { key: 'specialRequirements', label: '特殊要求', completed: false }
]

export function CourseCreationPage() {
  const navigate = useNavigate()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [courseInfo, setCourseInfo] = useState<CourseInfo>({
    courseType: '',
    topic: '',
    description: '',
    studentAge: 0,
    studentCount: 0,
    duration: '',
    specialRequirements: ''
  })

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '您好！我是PBL课程设计AI助手。让我来引导您创建一个优秀的项目式学习课程。\n\n首先，请告诉我您想创建什么类型的课程？\n\n可选类型：\n• STEM（科学、技术、工程、数学）\n• 人文社科\n• 艺术创作\n• 综合实践\n• 其他（请具体说明）',
      timestamp: new Date()
    }
  ])

  const [inputValue, setInputValue] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  const [isCollectionComplete, setIsCollectionComplete] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const addMessage = (role: 'assistant' | 'user', content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }

  const getNextQuestionPrompt = (step: number) => {
    const prompts = [
      '很好！现在请告诉我您的课程主题是什么？例如："环保与可持续发展"、"智能家居设计"等。',
      '非常棒！接下来请详细描述一下这个课程的内容和目标。您希望学生通过这个项目学到什么？',
      '了解了！这个课程主要面向多大年龄的学生？请输入具体的年龄，例如：12（表示12岁左右的学生）。',
      '好的！预计会有多少名学生参与这个课程？请输入具体的人数。',
      '明白了！这个课程计划持续多长时间？例如："4周"、"一个学期"、"2个月"等。',
      '最后一个问题：对这个课程有什么特殊要求吗？比如特定的技术设备、实验环境、合作伙伴等。如果没有特殊要求，可以回复"无"。'
    ]
    // step 1->0, step 2->1, 等等，因为step 0是课程类型（初始消息）
    return prompts[step - 1] || ''
  }

  const processUserInput = (userInput: string) => {
    const stepKeys = ['courseType', 'topic', 'description', 'studentAge', 'studentCount', 'duration', 'specialRequirements']
    const currentKey = stepKeys[currentStep]

    if (currentKey) {
      setCourseInfo(prev => ({
        ...prev,
        [currentKey]: currentKey === 'studentAge' || currentKey === 'studentCount'
          ? parseInt(userInput) || 0
          : userInput
      }))

      if (currentStep < stepKeys.length - 1) {
        const nextStep = currentStep + 1
        setCurrentStep(nextStep)
        setTimeout(() => {
          addMessage('assistant', getNextQuestionPrompt(nextStep))
        }, 500)
      } else {
        setIsCollectionComplete(true)
        setTimeout(() => {
          addMessage('assistant', '太棒了！我已经收集到了所有必要的信息。\n\n现在我将为您创建PBL课程设计方案。点击下方的"开始创建课程"按钮，我将引导您进入设计工作台，自动生成课程节点和内容。\n\n您准备好开始了吗？')
        }, 500)
      }
    }
  }

  const handleSendMessage = () => {
    if (!inputValue.trim() || isProcessing) return

    addMessage('user', inputValue.trim())

    if (!isCollectionComplete) {
      setIsProcessing(true)
      setTimeout(() => {
        processUserInput(inputValue.trim())
        setIsProcessing(false)
      }, 300)
    }

    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleStartCreation = () => {
    // 这里将导航到设计工作台，并传递课程信息
    const courseData = encodeURIComponent(JSON.stringify(courseInfo))
    navigate(`/design?data=${courseData}`)
  }

  const getCompletedStepsCount = () => {
    return Object.entries(courseInfo).filter(([key, value]) => {
      if (key === 'specialRequirements') return true // 特殊要求可以为空
      return value !== '' && value !== 0
    }).length
  }

  const getProgressPercentage = () => {
    const totalSteps = 7
    const completedSteps = getCompletedStepsCount()
    return Math.min((completedSteps / totalSteps) * 100, 100)
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
            <h1 className="text-xl font-semibold text-gray-900">创建新课程</h1>
          </div>

          {/* Progress Indicator */}
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              信息收集进度: {getCompletedStepsCount()}/7
            </div>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Left Panel - Course Info Preview */}
        <div className="w-1/3 bg-white border-r border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">课程信息预览</h2>

          <div className="space-y-4">
            {COLLECTION_STEPS.map((step, index) => {
              const value = courseInfo[step.key as keyof CourseInfo]
              const isCompleted = value !== '' && value !== 0

              return (
                <div key={step.key} className="flex items-start space-x-3">
                  <div className={`mt-1 w-5 h-5 rounded-full flex items-center justify-center ${
                    isCompleted ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-3 h-3 text-green-600" />
                    ) : (
                      <span className="text-xs text-gray-400">{index + 1}</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{step.label}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      {isCompleted ? (
                        <span className="text-green-700">{String(value)}</span>
                      ) : (
                        <span className="text-gray-400">待填写</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {isCollectionComplete && (
            <div className="mt-8">
              <button
                onClick={handleStartCreation}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                开始创建课程
              </button>
            </div>
          )}
        </div>

        {/* Right Panel - AI Chat */}
        <div className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-indigo-600" />
                  </div>
                )}

                <div
                  className={`max-w-md rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-900'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.content}
                  </div>
                  <div className="text-xs opacity-70 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-gray-600" />
                  </div>
                )}
              </div>
            ))}

            {isProcessing && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-indigo-600" />
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">AI正在思考...</div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          {!isCollectionComplete && (
            <div className="border-t border-gray-200 p-6">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="请输入您的回答..."
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  disabled={isProcessing}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isProcessing}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}