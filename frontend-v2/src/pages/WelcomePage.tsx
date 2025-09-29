import { useNavigate } from 'react-router-dom'
import { Plus, BookOpen, Users, Clock, Target } from 'lucide-react'

export function WelcomePage() {
  const navigate = useNavigate()

  const handleCreateCourse = () => {
    navigate('/create')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-indigo-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">PBLCourseAgent</h1>
              <span className="ml-2 text-sm text-gray-500">AI驱动的PBL课程设计助手</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            智能化PBL课程设计平台
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            通过AI助手引导，快速创建高质量的项目式学习（PBL）课程。
            从项目定义到评估框架，再到学习蓝图，一站式完成课程设计。
          </p>

          {/* Main CTA Button */}
          <button
            onClick={handleCreateCourse}
            className="inline-flex items-center px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
          >
            <Plus className="h-6 w-6 mr-2" />
            创建新课程
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <Target className="h-8 w-8 text-indigo-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">智能引导设计</h3>
            </div>
            <p className="text-gray-600">
              AI助手引导您逐步输入课程信息，确保课程设计的完整性和专业性。
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <Users className="h-8 w-8 text-green-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">个性化定制</h3>
            </div>
            <p className="text-gray-600">
              根据学生年龄、人数、课程主题等信息，自动生成适合的PBL方案。
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <Clock className="h-8 w-8 text-purple-600 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900">高效创建</h3>
            </div>
            <p className="text-gray-600">
              自动化工作流程，从项目基础到学习蓝图，快速生成完整课程方案。
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-lg p-8 shadow-md">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            课程设计流程
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-indigo-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                <span className="text-indigo-600 font-bold text-lg">1</span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">信息收集</h4>
              <p className="text-gray-600 text-sm">
                AI助手引导您输入课程类型、主题、学生信息等基础信息
              </p>
            </div>

            <div className="text-center">
              <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                <span className="text-green-600 font-bold text-lg">2</span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">自动创建</h4>
              <p className="text-gray-600 text-sm">
                系统自动在画布上创建课程节点，生成项目基础定义和评估框架
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                <span className="text-purple-600 font-bold text-lg">3</span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">确认完善</h4>
              <p className="text-gray-600 text-sm">
                逐步确认每个阶段的内容，修改完善，最终生成完整课程方案
              </p>
            </div>
          </div>
        </div>

        {/* Recent Courses Section (Placeholder) */}
        <div className="mt-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">最近的课程</h3>
          <div className="bg-white rounded-lg p-6 shadow-md">
            <p className="text-gray-500 text-center py-8">
              您还没有创建任何课程。点击上方"创建新课程"开始设计您的第一个PBL课程！
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500">
            © 2024 PBLCourseAgent. AI驱动的PBL课程设计助手
          </p>
        </div>
      </footer>
    </div>
  )
}