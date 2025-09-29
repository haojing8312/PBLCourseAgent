# **产品设计文档 (PRD): Project Genesis AI (MVP)**

**文档版本:** 1.1
**状态:** 完整版
**创建日期:** 2025年9月28日
**最后更新:** 2025年9月28日
**作者:** 郝敬 & gemini & claude code

---

## **目录**

1. [概述与简介](#10-概述与简介-overview--introduction)
2. [MVP目标与成功指标](#20-mvp目标与成功指标-goals--success-metrics)
3. [核心功能与用户故事](#30-核心功能与用户故事-features--user-stories)
4. [系统设计与技术要求](#40-系统设计与技术要求)
5. [MVP范围之外](#50-mvp范围之外-out-of-scope)
6. [后端 AI 引擎 - 详细实现逻辑](#60-后端-ai-引擎---详细实现逻辑)
7. [质量保证基准案例](#70-质量保证基准案例-qa-benchmark-case)
8. [实施路线图与里程碑](#80-实施路线图与里程碑)
9. [风险评估与缓解策略](#90-风险评估与缓解策略)

---

### **1.0 概述与简介 (Overview & Introduction)**

#### **1.1 产品愿景 (Vision)**
赋能每一位教育者，使其能够借助AI的力量，轻松创造出世界级的、以项目式学习（PBL）为核心的未来课程。

#### **1.2 问题陈述 (Problem Statement)**
现代教育强调培养学生解决问题、协作和创新的能力，PBL是实现这一目标的最佳教学法之一。然而，设计一门高质量的PBL课程，尤其是结合了前沿AI工具的课程，对绝大多数一线教师而言，存在三大障碍：
1.  **时间成本高:** 从构思到制定详细方案，需要数十小时的投入。
2.  **专业门槛高:** 需要深入理解PBL教学法和复杂的AI工具。
3.  **创新压力大:** 持续构思与现实世界接轨的、有趣的项目主题极具挑战。

这导致许多有创新意愿的机构和教师望而却步，无法将最新的技术和教学理念带给学生。

#### **1.3 目标用户画像 (User Persona)**

* **姓名:** Evelyn Reed
* **角色:** 传统培训机构的老师（如美术培训机构、少儿编程培训机构、音乐培训机构）
* **背景:** 32岁，拥有5年儿童美术教学经验。对传统绘画教学感到一丝厌倦，渴望在课程中融入更多科技和创意元素。她听说过AI绘画，自己也尝试玩过几次Midjourney，但感觉prompt很难掌握。她希望开设一个“AI奇幻生物设计”的周末短训营，但面对从零开始设计课程，她感到毫无头绪，担心自己无法掌控课堂。
* **目标 (Goals):**
    * 快速设计出一个专业的、有趣的AI艺术主题PBL工作坊方案。
    * 获得一份能“照着做”的详细流程，让自己在上课时充满信心。
    * 了解如何将AI绘画工具自然地融入到自己的艺术课程中。
* **痛点 (Frustrations):**
    * “我不知道一个好的PBL课程应该包含哪些部分。”
    * “我没有时间去研究各种复杂的AI工具和PBL理论。”
    * “我很怕自己设计的课程不够专业，孩子们会觉得无聊。”

#### **1.4 MVP核心价值主张 (Core Value Proposition)**
**Project Genesis AI** 是一款智能PBL课程设计引擎。您只需输入您的创意火花，我们将为您生成一份由顶级教学设计专家和AI共同打造的、结构完整、步骤清晰的PBL课程方案，让您轻松变身课程设计大师。

---

### **2.0 MVP目标与成功指标 (Goals & Success Metrics)**

#### **2.1 产品目标**
1.  **验证核心引擎:** 验证我们基于LLM Prompt链的课程生成逻辑能否产出用户认可的高质量内容。
2.  **收集早期反馈:** 获取第一批种子用户对产品价值、易用性和输出内容质量的真实反馈。
3.  **测试市场需求:** 初步判断市场对AI驱动的课程设计工具的接受度和付费意愿。

#### **2.2 成功指标 (KPIs)**
* **激活率 (Activation Rate):** > 60% 的访问用户成功生成至少一份课程方案。
* **用户满意度 (CSAT):** 在生成结果页设置一个简单的“这份方案对您有用吗？”（1-5星）评分，目标平均分 > 4.0。
* **核心功能使用率:** “下载方案”按钮的点击率，作为衡量方案实用性的间接指标。
* **定性反馈数量:** 通过反馈渠道，在一周内收集到至少20条有价值的定性用户建议。

---

### **3.0 核心功能与用户故事 (Features & User Stories)**

#### **Epic: AI驱动的PBL课程方案一键生成**

**As a** 缺乏PBL设计经验的教师,
**I want to** 输入我的课程主题和基本要求，快速得到一份详尽的、可执行的课程方案,
**So that I can** 节省大量的备课时间，并充满信心地为我的学生提供一堂高质量的PBL课程。

---

**User Story 1: 输入课程设计参数**
**As a** 用户, **I want to** 在一个清晰的界面上输入我构思的课程核心要素, **so that** AI可以理解我的设计意图。

* **功能需求 (Functional Requirements):**
    * **FR-1.1:** 提供一个单页Web表单，包含以下输入字段：
        * `课程主题 (Project Title)`: 文本输入框 (示例: 我的超能分身)。
        * `课程概要 (Brief Summary)`: 文本区域 (示例: 孩子们想象平行宇宙的自己，并用AI创造出3D模型)。
        * `年龄段 (Age Group)`: 下拉选择 (示例: 6-8岁, 9-12岁, 13-15岁)。
        * `课程时长 (Duration)`: 下拉选择 (示例: 半天(4小时), 1天(8小时), 2天, 3天)。
        * `核心AI工具/技能 (Key AI Tools/Skills)`: 标签输入框，允许用户自由输入或选择预设标签 (示例: AI绘画, 3D打印, Suno)。
* **设计/UX说明:**
    * 每个字段都应有清晰的标签和简短的解释性文字或占位符。
    * 界面设计应极致简洁，避免任何不必要的干扰，让用户聚焦于内容输入。

**User Story 2: 查看智能生成的课程方案**
**As a** 用户, **I want to** 在点击生成后，看到一份结构清晰、内容专业的课程方案, **so that** 我可以直接使用或在此基础上进行微调。

* **功能需求 (Functional Requirements):**
    * **FR-2.1:** 用户点击“生成方案”按钮后，系统应显示一个加载状态，以管理用户等待预期。加载文案应友好且与产品调性相关 (例如: "正在连接AI教学专家...", "正在为您的创意构建蓝图...")。
    * **FR-2.2:** 后端AI引擎需按照“逆向设计”逻辑，生成包含以下标准模块的课程方案：
        1.  **封面页:** 课程主题、建议年龄、时长。
        2.  **项目简介:** 驱动性问题、最终公开成果、核心学习目标。
        3.  **评估方案:** 总结性评估量规(Rubric)、形成性评估检查点。
        4.  **详细流程:** 按时间线分解的教学步骤（包含教师活动、学生活动、所需材料）。
        5.  **教师准备清单:** 课前物料准备和教师需具备的技能。
    * **FR-2.3:** 生成的方案将展示在一个干净、易于阅读的Web页面上。
    * **FR-2.4:** 在结果页面提供“复制到剪贴板”和“下载为PDF”功能。
* **设计/UX说明:**
    * 方案的排版至关重要，使用清晰的标题、列表和表格来组织内容。
    * 评估量规(Rubric)必须以表格形式呈现。
    * 下载的PDF应保持良好的格式，并可带有产品Logo。

**User Story 3: 提供产品反馈**
**As a** 早期用户, **I want to** 能够方便地对我生成的方案质量和产品体验提供反馈, **so that** 产品可以变得更好。

* **功能需求 (Functional Requirements):**
    * **FR-3.1:** 在结果页面放置一个显眼的、非侵入式的反馈模块，包含1-5星评分和可选的评论框。
    * **FR-3.2:** 在网站页脚提供一个“联系我们/反馈”的链接。

---

### **4.0 系统设计与技术要求**

#### **4.1 技术架构**
* **前端:** 建议使用React现代SPA框架，确保良好的交互体验。
* **后端:** 建议使用Python，以便无缝集成主流AI库(`openai`以及兼容openai格式的大模型，如openrouter)。
* **AI核心:**
    * 明确使用**GPT-4o**的API。
    * 核心逻辑为**"Prompt链"或串行化的Agent工作流**，严格遵循**目标定义 -> 评估设计 -> 流程规划**的顺序，确保生成内容的逻辑性和专业性。
    * **Prompt中必须包含角色扮演指令** (例如: "你是一位顶级的、拥有15年经验的PBL教学设计师...") 以提升输出质量。

#### **4.2 性能指标**
为确保良好的用户体验并有效监控系统性能，总生成时间 `T_total` (目标 < 600秒) 分解如下：

* **T_agent1 (项目基础定义):** 目标 < 20秒。此阶段Prompt相对简单，输出较少，响应应最快。
* **T_agent2 (评估框架设计):** 目标 < 25秒。此阶段涉及逻辑推理和表格生成，耗时会稍长。
* **T_agent3 (学习蓝图生成):** 目标 < 40秒。此阶段是内容生成的核心，输出文本量最大，耗时最长是正常的。
* **T_processing (后端处理):** 目标 < 5秒。这是各阶段之间数据处理和最终文档渲染的时间，应极快。

**监控策略:** 对每次API调用的耗时进行日志记录，若任一阶段的P95延迟（95%的请求耗时）超出目标值，则触发警报，需对相应Prompt进行优化。

#### **4.3 非功能性需求**
* **性能:** MVP不限制时间，要保证生成方案的质量。
* **可扩展性:** 后端Prompt链的设计应模块化，便于未来添加新的生成步骤或替换模型。
* **成本:** 监控API调用成本，在Prompt设计时兼顾质量与Token消耗。

---

### **5.0 MVP范围之外 (Out of Scope)**

为确保快速上线和聚焦核心价值，以下功能**不包含**在MVP版本中：
* **用户账户系统:** 无需注册/登录，所有生成都是临时的。
* **方案保存与编辑:** 生成的方案是最终版本，用户需通过下载或复制来保存。
* **交互式/对话式设计:** 所有输入通过一次性表单完成。
* **多语言支持:** MVP仅支持中文。
* **支付与订阅功能:** MVP阶段完全免费。

---

### **6.0 后端 AI 引擎 - 详细实现逻辑**

本部分详细阐述了构成核心生成引擎的三个AI Agent的内部设计、核心Prompt、输入与输出样例。

#### **Agent 1: 项目基础定义 (Project Foundation Agent)**

  * **设计逻辑:** 此Agent是工作流的起点，负责将用户的模糊创意转化为一个结构化的、符合PBL基本原则的项目框架。它的任务是“发散”与“收敛”，既要激发创意，又要将其固化为明确的目标。
  * **核心Prompt:**
    ```prompt
    # ROLE & CONTEXT
    You are "Genesis One", an expert-level Instructional Designer specializing in Project-Based Learning (PBL) and the "Understanding by Design" (UbD) framework. You are designing a short-term workshop for a teacher who is not a PBL expert. Your tone should be creative, clear, and encouraging.

    # INSTRUCTION
    Based on the user's input JSON, generate a foundational project plan. The output MUST be a valid JSON object following the specified schema.

    # SCHEMA
    {
      "drivingQuestion": "A concise, open-ended, and engaging question that will drive the entire project.",
      "publicProduct": {
        "description": "A tangible or digital product that students will create and share. Describe what it is and who the audience is.",
        "components": ["List of individual items that make up the final product."]
      },
      "learningObjectives": {
        "hardSkills": ["List of 3-4 specific technical or tool-based skills students will learn."],
        "softSkills": ["List of 2-3 key 21st-century skills (e.g., collaboration, critical thinking) this project will cultivate."]
      }
    }

    # USER INPUT
    {{userInputJson}}
    ```
  * **样例输入 (JSON):**
    ```json
    {
      "theme": "我的超能分身",
      "summary": "孩子们想象在平行宇宙的一个拥有超能力的自己的样子，最终制作一个身份卡和3D模型",
      "ageGroup": "9-12岁",
      "duration": "1天(8小时)",
      "keyTools": ["AI对话", "AI绘画", "AI 3D建模", "3D打印"]
    }
    ```
  * **样例输出 (JSON):**
    ```json
    {
      "drivingQuestion": "如果我们能用AI赋予想象力实体，我们要如何创造一个代表最强自己的'超能分身'并向世界展示它？",
      "publicProduct": {
        "description": "一个完整的'超能分身'展示套件，将在课程结束时向家长和同学进行一个小型'英雄博览会'展示。",
        "components": [
          "一张设计精美的实体'超能分身'身份卡",
          "一个3D打印出来的'超能分身'实体模型"
        ]
      },
      "learningObjectives": {
        "hardSkills": [
          "使用AI对话工具(如Kimi)进行创意构思和故事写作。",
          "掌握基本的AI绘画提示词工程(Prompt Engineering)来创造角色形象。",
          "使用AI工具(如Luma AI)将2D图像转换为3D模型。",
          "了解3D打印的基本流程（从切片到打印）。"
        ],
        "softSkills": [
          "问题解决能力：当AI生成结果不理想时，如何调整思路和方法。",
          "创造性表达：将个人抽象的想法转化为具体的、可视化的艺术作品。",
          "沟通与展示：清晰地向他人介绍自己的作品和创作理念。"
        ]
      }
    }
    ```

-----

#### **Agent 2: 评估框架设计 (Assessment Framework Agent)**

  * **设计逻辑:** 此Agent承接Agent 1的输出，扮演“质量保证”的角色。它依据已确定的学习目标和成果，设计出一套公正、清晰的评估体系，确保学习效果是可衡量的。
  * **核心Prompt:**
    ```prompt
    # ROLE & CONTEXT
    You are "Genesis Two", a meticulous curriculum evaluator. Your task is to create a comprehensive assessment framework based on the provided project foundation. The framework must be practical for a non-expert teacher to use.

    # INSTRUCTION
    Based on the project foundation JSON, generate an assessment framework. The output MUST be a valid JSON object following the specified schema. The rubric descriptions should be clear, positive, and action-oriented.

    # SCHEMA
    {
      "summativeRubric": [
        {
          "dimension": "The skill or quality being measured (e.g., '创意构思').",
          "level_1_desc": "Description for '新手' level.",
          "level_2_desc": "Description for '学徒' level.",
          "level_3_desc": "Description for '工匠' level.",
          "level_4_desc": "Description for '大师' level."
        }
      ],
      "formativeCheckpoints": [
        {
          "name": "The name of the checkpoint (e.g., '创意概念审核').",
          "triggerTime": "When this check happens (e.g., '上午结束前').",
          "purpose": "What the teacher should check for."
        }
      ]
    }

    # PROJECT FOUNDATION
    {{agent1OutputJson}}
    ```
  * **样例输入 (JSON):** Agent 1的样例输出。
  * **样例输出 (JSON):**
    ```json
    {
      "summativeRubric": [
        {
          "dimension": "创意构思与故事性",
          "level_1_desc": "角色设定较为基础，故事线索简单。",
          "level_2_desc": "角色有独特的超能力设定和基本的背景故事。",
          "level_3_desc": "角色设定完整，背景故事丰富且具有逻辑性。",
          "level_4_desc": "角色设定极富想象力，背景故事新颖且能引发情感共鸣。"
        },
        {
          "dimension": "AI工具应用与技术实现",
          "level_1_desc": "能在家师帮助下完成AI工具的基本操作。",
          "level_2_desc": "能独立使用AI工具生成基本符合要求的图像和模型。",
          "level_3_desc": "能通过多次尝试和调整，熟练运用AI工具优化产出质量。",
          "level_4_desc": "能创造性地结合多个AI工具，实现超越预期的技术效果。"
        },
        {
          "dimension": "最终成果完整性与美学",
          "level_1_desc": "完成了部分最终成果组件。",
          "level_2_desc": "完成了所有成果组件，但细节和排版有待提升。",
          "level_3_desc": "最终成果完整、整洁，具有良好的视觉呈现效果。",
          "level_4_desc": "最终成果不仅完整，且在设计上表现出强烈的个人风格和美感。"
        }
      ],
      "formativeCheckpoints": [
        {
          "name": "AI形象初稿'画廊漫步'",
          "triggerTime": "午饭前",
          "purpose": "检查学生是否已生成核心的角色形象，并组织同伴互评，收集初步反馈，以便下午进行迭代。"
        },
        {
          "name": "3D模型可打印性检查",
          "triggerTime": "下午3点左右",
          "purpose": "在发送到打印机前，老师快速检查每个学生的3D模型文件是否完整、无明显破损，确保打印成功率。"
        }
      ]
    }
    ```

-----

#### **Agent 3: 学习蓝图生成 (Learning Blueprint Agent)**

  * **设计逻辑:** 这是最终的集大成者。它将前两个Agent的输出（“是什么”和“如何衡量”）整合成一个详细的、可执行的“如何做”的行动方案。它必须将所有内容翻译成新手老师能理解和执行的语言。
  * **核心Prompt:** (此Prompt最复杂)
    ```prompt
    # ROLE & CONTEXT
    You are "Genesis Three", a master teacher and facilitator with 20 years of classroom experience. You excel at writing lesson plans that are so clear, even a substitute teacher could run them perfectly. Your language is simple, direct, and full of practical tips.

    # INSTRUCTION
    Synthesize the Project Foundation and Assessment Framework into a detailed, step-by-step lesson plan for a full-day workshop. The total duration is {{duration}}. The output MUST be a valid JSON object following the specified schema. Ensure the timeline is logical and includes breaks. For each activity, provide a clear 'teacherScript' and 'studentTask'.

    # SCHEMA
    {
      "teacherPrep": {
        "materialList": ["List of all physical and digital materials needed."],
        "skillPrerequisites": ["List of skills the teacher must be comfortable with before the class."]
      },
      "timeline": [
        {
          "timeSlot": "e.g., '9:00 AM - 9:30 AM'",
          "activityTitle": "e.g., '破冰与项目启动'",
          "teacherScript": "A brief script or key talking points for the teacher.",
          "studentTask": "A clear description of what students should be doing.",
          "materials": ["Specific materials for this activity."]
        }
      ]
    }

    # PROJECT FOUNDATION
    {{agent1OutputJson}}

    # ASSESSMENT FRAMEWORK
    {{agent2OutputJson}}
    ```
  * **样例输入 (JSON):** Agent 1和Agent 2的样例输出的组合。
  * **样例输出 (JSON):** 

```json
{
  "teacherPrep": {
    "materialList": [
      "每位学生一台性能达标、网络通畅的电脑",
      "为所有学生提前注册并测试好AI对话、AI绘画、AI 3D建模的软件账号",
      "至少2台经过调试和校准的3D打印机，以及足量的PLA等安全耗材",
      "A4卡纸（用于制作身份卡）、彩笔、剪刀、胶水",
      "一个教师提前制作好的“超能分身”完整样品（身份卡+3D模型）",
      "投影仪和音响设备",
      "学生分组名单（建议每组3-4人，便于协作）"
    ],
    "skillPrerequisites": [
      "熟练操作本项目中使用的三款核心AI软件。",
      "掌握3D打印机的基本操作，包括启动、换料、从电脑发送打印任务，以及处理简单的堵头或翘边问题。",
      "具备引导学生进行创意头脑风暴的能力。",
      "熟悉如何组织学生进行积极、有建设性的同伴互评（Peer Feedback）。"
    ]
  },
  "timeline": [
    {
      "timeSlot": "9:00 AM - 9:30 AM",
      "activityTitle": "破冰与项目启动：英雄集结令",
      "teacherScript": "“欢迎来到今天的'超能分身'创造营！在开始之前，我们先来想象一下：如果明天醒来你可以随机获得一个超能力，但这个能力可能非常奇葩，比如‘让所有香蕉立刻成熟’，你该怎么办？... 好了，玩笑开完了。今天，我们不靠随机，而是要亲手用AI这个魔法工具，为自己设计最酷的超能分身！看，这是我为自己设计的...” (展示样品，激发兴趣，并正式提出驱动性问题)",
      "studentTask": "参与破冰讨论，分享自己的奇思妙想。观察并触摸老师的样品，建立对最终目标的具象认知和兴奋感。",
      "materials": ["教师样品", "投影仪"]
    },
    {
      "timeSlot": "9:30 AM - 10:30 AM",
      "activityTitle": "技能工坊一：与AI对话，唤醒你的英雄",
      "teacherScript": "“一个英雄的强大，首先源于其内核——他的故事和能力。接下来，我们将与一位‘AI创意大师’对话，挖掘出我们分身的独特设定。我来演示如何向AI提问，才能获得最有创意的回答...” (演示如何使用Kimi/ChatGPT进行头脑风暴，并指导学生开始在身份卡草稿上记录想法)",
      "studentTask": "跟随老师学习AI对话技巧。独立使用AI对话工具，构思自己分身的名字、背景故事、超能力、性格特点等，并将关键信息填写到身份卡草稿模板上。",
      "materials": ["电脑", "AI对话软件", "身份卡草稿模板"]
    },
    {
      "timeSlot": "10:30 AM - 11:45 AM",
      "activityTitle": "技能工坊二：AI绘画，赋予英雄形象",
      "teacherScript": "“文字已经描绘出英雄的灵魂，现在我们要赋予他血肉！我们会学习一种新的咒语——提示词(Prompt)，让AI画师为我们精准地画出英雄的模样。看我的咒语：‘一个10岁的男孩，赛博朋克风格...’”(演示Midjourney/SD，讲解核心关键词、风格词和构图词的使用方法)",
      "studentTask": "学习编写有效的AI绘画提示词。根据自己的角色设定，反复尝试、迭代，生成并挑选出最满意的分身形象。将最终图片保存下来。",
      "materials": ["电脑", "AI绘画软件", "之前完成的身份卡草稿"]
    },
    {
      "timeSlot": "11:45 AM - 12:00 PM",
      "activityTitle": "检查点一：AI形象初稿“画廊漫步”",
      "teacherScript": "“各位伟大的创造者，请将你们最得意的作品发送到投屏上。现在，让我们站起来，像逛画廊一样，欣赏彼此的作品。你可以为你最喜欢的3个作品贴上一颗小星星贴纸，并可以留下一句赞美或建议。”(组织同伴互评)",
      "studentTask": "将自己的作品投屏展示。安静地欣赏他人的作品，并使用贴纸和便签进行积极的反馈。观察别人的优点，思考自己下午可以如何改进。",
      "materials": ["投影仪", "便签", "星星贴纸"]
    },
    {
      "timeSlot": "12:00 PM - 1:00 PM",
      "activityTitle": "午餐与能量补充",
      "teacherScript": "“大脑和AI高速运转了一上午，现在是为我们自己补充能量的时间！大家下午见！”",
      "studentTask": "吃饭，休息，自由交流。",
      "materials": []
    },
    {
      "timeSlot": "1:00 PM - 2:30 PM",
      "activityTitle": "技能工坊三：从2D到3D，英雄破壁而出",
      "teacherScript": "“欢迎回来！我们的英雄现在还存在于平面的屏幕中，下午的任务是让他‘走出来’，站到我们的桌子上！我们将学习如何用AI将2D图片转换为3D模型。”(演示Luma AI等工具，强调图片作为输入的要点，以及模型生成后如何进行简单的旋转和检查)",
      "studentTask": "将上午生成的2D角色形象导入AI 3D建模工具。生成3D模型，下载模型文件（如.obj或.stl格式）。如果遇到问题，可以先尝试优化2D图片或向老师求助。",
      "materials": ["电脑", "AI 3D建模软件", "上午保存的角色图片"]
    },
    {
      "timeSlot": "2:30 PM - 3:00 PM",
      "activityTitle": "3D打印准备与启动",
      "teacherScript": "“大家注意，3D打印就像一个漫长的‘召唤仪式’，需要一些时间。现在，我会演示如何将你们的3D模型文件导入切片软件，进行设置，然后发送给打印机。我会优先帮助已经完成模型的同学开始打印。”(演示切片软件和打印机操作)",
      "studentTask": "将自己的3D模型文件交给老师，或者在老师指导下自行导入切片软件。观察打印机开始工作的过程。",
      "materials": ["3D模型文件", "切片软件（如Cura）", "3D打印机"]
    },
    {
      "timeSlot": "3:00 PM - 3:15 PM",
      "activityTitle": "检查点二：3D模型可打印性检查",
      "teacherScript": "“在所有人的打印任务都开始后，我会快速检查一遍队列。这个检查点是为了确保每个模型都大概率能成功打印出来，避免浪费时间和材料。”",
      "studentTask": "确认自己的打印任务已在队列中。可以回到座位，开始下一个任务。",
      "materials": ["3D打印机任务队列"]
    },
    {
      "timeSlot": "3:15 PM - 4:15 PM",
      "activityTitle": "创作冲刺：完善身份卡与准备分享",
      "teacherScript": "“在等待英雄模型‘降临’的时候，我们来完成最后一件重要的事——制作一张精美的、可以永久收藏的英雄身份卡！同时，思考一下，你将如何向大家介绍你的这位酷炫分身？”",
      "studentTask": "使用卡纸、彩笔和上午打印出的角色图片，精心设计并制作实体的身份卡。可以撰写一个简短的发言稿（30-60秒），准备在成果展上分享自己的创作。",
      "materials": ["卡纸", "彩笔", "剪刀", "胶水", "打印出的角色图片"]
    },
    {
      "timeSlot": "4:15 PM - 4:50 PM",
      "activityTitle": "最终成果展：“第一届超能英雄博览会”",
      "teacherScript": "“先生们女士们，欢迎来到我们的英雄博览会！现在，有请我们的创造者，带着他们的英雄身份卡和刚刚新鲜出炉的3D模型，逐一上台，向我们隆重介绍他们的超能分身！”(营造仪式感，主持展示会)",
      "studentTask": "带着自己的两件套最终成果（身份卡+3D模型）上台，自信地进行1分钟的分享。作为观众时，认真倾听，并为每一位同学的精彩创作鼓掌。",
      "materials": ["所有学生的最终成果", "投影仪（可选，用于展示身份卡细节）"]
    },
    {
      "timeSlot": "4:50 PM - 5:00 PM",
      "activityTitle": "复盘与结营：英雄的思考",
      "teacherScript": "“今天，我们每个人都完成了一件了不起的创造。在结束之前，我想问大家一个问题：在和AI合作创造的过程中，你觉得AI更像你的什么？一个听话的工具？一个有想法的伙伴？还是一个需要你耐心教导的学生？为什么？”(引导学生进行更深层次的反思)",
      "studentTask": "分享自己与AI协作的感受和收获。收拾好自己的作品和工位，带着满满的成就感结束一天的创造之旅。",
      "materials": []
    }
  ]
}
```

---

### **7.0 质量保证基准案例 (QA Benchmark Case)**

用于验证生成器输出质量的"黄金标准"案例。

#### **7.1 基准案例输入**

* **课程主题:** AI乐队制作人
* **课程概要:** 学生将扮演一个乐队制作人的角色，使用AI工具为一首预设的歌词创作旋律、编曲，并制作一个简单的歌词MV。
* **年龄段:** 13-15岁
* **课程时长:** 2天
* **核心AI工具/技能:** Suno (AI音乐), Runway (AI视频), Canva (平面设计)

#### **7.2 "黄金标准"方案**

此基准案例的完整"黄金标准"方案已由专业教学设计师手动撰写，包含以下标准模块：

**封面页信息：**
- 课程主题：AI乐队制作人 (AI Band Producer)
- 课程标语：当文字遇上代码，用AI为诗歌谱写心灵的MV
- 建议年龄段：13-15岁
- 课程时长：2天 (约16学时)

**驱动性问题：**
"作为一名新生代的音乐制作人，我们如何仅凭一段文字和强大的AI工具，就能创作出一首能触动人心的歌曲，并为其打造一场完整的、专业的视听发布体验？"

**最终公开成果：**
- 一首完整的歌曲 (MP3)：时长1-2分钟
- 一个歌词MV (MP4)：AI生成的动态视觉画面组成的音乐视频
- 一张数字专辑封面：体现歌曲情绪和风格的专辑封面

**评估量规：**
包含4个维度的专业评估标准：音乐创意与情感表达、视觉叙事与MV制作、AI工具整合与流畅度、项目完成度与专业性，每个维度分为4个等级。

**详细的2天教学流程：**
- Day 1：从文字到旋律，包含歌词解读、Suno技能工坊、Demo试听会等
- Day 2：从画面到影片，包含Runway技能工坊、MV剪辑合成、最终发布会等

完整的黄金标准方案详见：`docs/黄金标准方案.md`

**质量验证标准：**
AI生成的方案应在结构完整性、内容专业性、可执行性三个方面达到黄金标准的80%以上匹配度。

---

### **8.0 实施路线图与里程碑**

#### **8.1 开发阶段**
- **阶段1 (Week 1-2):** 核心AI引擎开发和Prompt优化
- **阶段2 (Week 3):** 前端界面开发和集成
- **阶段3 (Week 4):** 测试、优化和质量保证

#### **8.2 验证里程碑**
- **里程碑1:** 基准案例通过率达到80%
- **里程碑2:** 用户测试满意度达到4.0分以上
- **里程碑3:** 系统性能达到目标指标

---

### **9.0 风险评估与缓解策略**

#### **9.1 技术风险**
- **风险:** AI API响应时间不稳定
- **缓解:** 实施重试机制和超时处理

#### **9.2 质量风险**
- **风险:** 生成内容质量不一致
- **缓解:** 建立完善的Prompt工程和质量检测机制

#### **9.3 用户体验风险**
- **风险:** 用户界面复杂度过高
- **缓解:** 进行多轮用户测试和界面简化

---

**文档结束**