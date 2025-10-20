/**
 * UbD框架核心概念定义
 * 用于UI中的引导式说明和工具提示
 */

export interface UbdElement {
  symbol: string;
  name: string;
  shortDescription: string;
  fullDescription: string;
  examples: string[];
  commonMistakes: string[];
}

/**
 * UbD Stage One: 确定预期学习结果
 */
export const UBD_STAGE_ONE_ELEMENTS: Record<string, UbdElement> = {
  G: {
    symbol: 'G',
    name: '迁移目标 (Goals)',
    shortDescription: '学生将能够自主地将所学应用到新情境的能力',
    fullDescription:
      '迁移目标描述学生在无人指导下能够做什么。这是学习的终极目标——学生能够在新的、未曾遇到的情境中独立应用所学的知识和技能。',
    examples: [
      '✅ "学生将能够自主地设计AI解决方案来解决真实社区问题"',
      '✅ "学生将能够在新情境中批判性地分析技术的伦理影响"',
      '❌ "学生将学会Python编程"（这只是技能S，不是迁移目标）',
    ],
    commonMistakes: [
      '将具体技能误认为迁移目标',
      '目标过于狭窄，缺乏迁移性',
      '使用"学会"、"掌握"等动词，而非"能够自主地"',
    ],
  },

  U: {
    symbol: 'U',
    name: '持续理解 (Understandings)',
    shortDescription: '学生在忘记所有细节后，我们希望他们能永恒记住的核心思想',
    fullDescription:
      '持续理解是抽象的、可迁移的核心观念（big ideas）。这是学生在5年、10年后仍然记得的深刻洞察，而非具体的知识点或技能。理解超越了事实和技能，是对概念的深层把握。',
    examples: [
      '✅ "理解AI技术的双刃剑特性：它既能带来便利，也可能引发风险"',
      '✅ "认识到数据质量直接决定AI模型的有效性和公平性"',
      '✅ "意识到编程语言是表达思想的工具，而不仅仅是记忆语法"',
      '❌ "掌握Python编程基础"（这是知识K或技能S）',
      '❌ "了解机器学习算法"（这是知识K）',
    ],
    commonMistakes: [
      '将具体知识点（K）误认为持续理解',
      '将技能（S）误认为持续理解',
      '理解过于具体，无法迁移到其他情境',
      '包含具体工具名称而非普遍原理',
    ],
  },

  Q: {
    symbol: 'Q',
    name: '基本问题 (Essential Questions)',
    shortDescription: '开放性的、引发深度思考的问题，贯穿整个课程',
    fullDescription:
      '基本问题是没有唯一正确答案的开放性问题，旨在激发探究和争论。这些问题引导学生走向持续理解（U），课程结束时学生应该能够用U来回答Q。',
    examples: [
      '✅ "AI技术应该在多大程度上参与人类决策？"',
      '✅ "如何平衡技术创新的速度与伦理审查的必要性？"',
      '✅ "当AI系统出现偏见时，谁应该承担责任？"',
      '❌ "什么是机器学习？"（这是知识性问题，不是基本问题）',
      '❌ "如何使用ChatGPT？"（这是技能性问题，不够开放）',
    ],
    commonMistakes: [
      '问题有明确的单一答案',
      '问题过于具体，无法引发深度思考',
      '问题与持续理解（U）脱节',
    ],
  },

  K: {
    symbol: 'K',
    name: '应掌握的知识 (Knowledge)',
    shortDescription: '学生需要知道的事实、概念、原理、术语',
    fullDescription:
      '知识是领域特定的内容，包括事实、概念、术语、原理等。知识是"知道什么"的层面，是达成持续理解（U）和迁移目标（G）的基础，但不是终点。',
    examples: [
      '✅ "Python基本语法（变量、循环、函数）"',
      '✅ "机器学习的监督学习和非监督学习概念"',
      '✅ "提示工程的基本原则"',
      '✅ "AI伦理的关键概念（偏见、隐私、透明度）"',
    ],
    commonMistakes: [
      '知识列表过于庞大，学生无法全部掌握',
      '知识与U和G脱节，成为"为学知识而学知识"',
      '将抽象理解（U）误写为知识点',
    ],
  },

  S: {
    symbol: 'S',
    name: '应形成的技能 (Skills)',
    shortDescription: '学生需要能够做到的具体技能和能力',
    fullDescription:
      '技能是可迁移的能力，包括工具使用技能、实践技能、思维技能等。技能是"会做什么"的层面，是达成迁移目标（G）的关键。',
    examples: [
      '✅ "使用Python编写和调试代码"',
      '✅ "设计有效的AI提示词"',
      '✅ "批判性地分析和评估AI生成内容的质量"',
      '✅ "团队协作解决复杂问题"',
      '✅ "向非技术受众清晰展示技术方案"',
    ],
    commonMistakes: [
      '技能与知识（K）混淆',
      '技能过于狭窄，缺乏迁移性',
      '将抽象理解（U）误写为技能',
    ],
  },
};

/**
 * UbD Stage Two: 确定可接受的证据
 */
export const UBD_STAGE_TWO_GUIDE = {
  drivingQuestion: {
    title: '驱动性问题设计',
    description:
      '驱动性问题是整个PBL项目的核心挑战，必须基于真实情境、开放性、有挑战性、有明确产出物。',
    criteria: [
      '真实情境：基于真实世界问题，有明确的利益相关者',
      '开放性：无唯一答案，允许多种解决路径',
      '挑战性：需要综合运用G/U/Q/K/S',
      '明确产出：学生知道最终要创造什么，产出有真实受众',
    ],
    goodExample:
      '我们如何利用AI技术，为我们的社区创造一个解决实际问题的工具，同时确保技术的负责任使用？',
    badExample: '什么是AI？（知识性问题，不是驱动性问题）',
  },

  performanceTasks: {
    title: '表现性任务设计',
    description:
      '表现性任务是解决驱动性问题的关键里程碑，每个任务证明学生达成部分理解和技能。任务必须有真实情境、学生角色和具体产出物。',
    principles: [
      '分阶段支架：任务1探索 → 任务2设计 → 任务3开发 → 任务4展示',
      '真实情境：每个任务都有真实的context和学生角色',
      'UbD对齐：明确标注任务服务的U/S/K',
      '可评估性：每个任务必须有详细的rubric',
    ],
  },

  rubric: {
    title: '评估量规设计',
    description:
      '评估量规（Rubric）定义了如何评价学生的表现性任务。量规应该有3-5个维度，每个维度4个等级（卓越、熟练、发展中、初步），描述清晰可观察。',
    levels: ['卓越', '熟练', '发展中', '初步'],
    commonDimensions: [
      '内容理解（Understanding）：是否体现对U的深度理解',
      '技术执行（Technical Skill）：S的应用质量',
      '创造性（Creativity）：解决方案的创新性',
      '沟通表达（Communication）：展示和文档质量',
    ],
  },
};

/**
 * UbD Stage Three: 规划学习体验
 */
export const UBD_STAGE_THREE_GUIDE = {
  pblPhases: {
    title: 'PBL四阶段结构',
    description:
      '学习体验应该按照PBL的四个阶段组织：项目启动 → 知识与技能构建 → 开发与迭代 → 成果展示与反思',
    phases: [
      {
        name: '项目启动 (Launch)',
        purpose: '激发兴趣、建立需求、介绍驱动性问题',
        duration: '课程总时长的15-20%',
        keywords: ['Hook', 'Entry Event', 'Driving Question', 'KWL'],
      },
      {
        name: '知识与技能构建 (Build)',
        purpose: '系统学习完成项目所需的K和S',
        duration: '课程总时长的30-40%',
        keywords: ['Mini-lessons', 'Skill Practice', 'Research', 'Checkpoints'],
      },
      {
        name: '开发与迭代 (Develop)',
        purpose: '学生应用所学创造产出物，迭代改进',
        duration: '课程总时长的30-40%',
        keywords: ['Prototyping', 'Peer Review', 'Iteration', 'Milestones'],
      },
      {
        name: '成果展示与反思 (Present)',
        purpose: '展示学习成果，反思学习过程',
        duration: '课程总时长的10-15%',
        keywords: ['Public Presentation', 'Peer Evaluation', 'Reflection', 'Celebration'],
      },
    ],
  },

  wheretoPrinciples: {
    title: 'WHERETO原则',
    description:
      '每个学习活动应该至少服务于一个WHERETO原则，确保活动有明确的教学设计依据。',
    principles: [
      {
        code: 'W',
        name: 'Where & Why',
        description: '帮助学生了解学习目标和意义',
        example: '介绍驱动性问题，说明项目的真实价值',
      },
      {
        code: 'H',
        name: 'Hook',
        description: '激发兴趣和参与',
        example: '专家讲座、引人入胜的案例、挑战性问题',
      },
      {
        code: 'E',
        name: 'Equip & Experience',
        description: '提供学习所需的知识、技能和体验',
        example: '迷你课程、技能训练、资源探索',
      },
      {
        code: 'R',
        name: 'Rethink & Revise',
        description: '引导反思和改进',
        example: '同伴评审、迭代改进、反思日志',
      },
      {
        code: 'E',
        name: 'Explore & Enable',
        description: '鼓励探究和自主学习',
        example: '开放性研究任务、学生选择',
      },
      {
        code: 'T',
        name: 'Tailor',
        description: '个性化和差异化教学',
        example: '分层任务、学生选择主题、灵活分组',
      },
      {
        code: 'O',
        name: 'Organize & Optimize',
        description: '优化学习流程和资源',
        example: '清晰的时间表、工具准备、分组策略',
      },
    ],
  },
};

/**
 * UbD框架总体说明
 */
export const UBD_FRAMEWORK_OVERVIEW = {
  title: 'Understanding by Design (UbD) 框架',
  subtitle: '逆向设计：以终为始',
  description:
    'UbD是一种课程设计方法，强调从学习目标出发，先确定"学生应该理解什么"，再设计"如何评估理解"，最后规划"如何帮助学生达成理解"。这种逆向设计确保教学活动始终服务于深度理解。',
  stages: [
    {
      stage: 1,
      name: '确定预期学习结果',
      question: '我们希望学生理解什么？',
      output: 'G/U/Q/K/S框架',
    },
    {
      stage: 2,
      name: '确定可接受的证据',
      question: '如何知道学生是否达成了理解？',
      output: '驱动性问题 + 表现性任务 + 评估量规',
    },
    {
      stage: 3,
      name: '规划学习体验',
      question: '如何帮助学生达成理解？',
      output: 'PBL四阶段学习蓝图 + WHERETO原则',
    },
  ],
  corePhilosophy:
    '教学活动是达成理解的手段，而非目的。我们不是为了"教完内容"，而是为了"学生真正理解"。',
};

/**
 * 用于前端展示的颜色配置
 */
export const UBD_ELEMENT_COLORS = {
  G: '#1890ff', // 蓝色 - Goals
  U: '#52c41a', // 绿色 - Understandings
  Q: '#faad14', // 橙色 - Questions
  K: '#722ed1', // 紫色 - Knowledge
  S: '#f5222d', // 红色 - Skills
};
