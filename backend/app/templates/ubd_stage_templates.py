"""
UbD 教案 Markdown 模板
根据 docs/UBD教案模板.md 构建的三阶段模板
"""


def get_stage_one_template() -> str:
    """
    获取阶段一模板：确定预期学习结果

    Returns:
        str: 阶段一的Markdown模板字符串
    """
    return """# 阶段一：确定预期学习结果

## 课标

{standards}

## G: 迁移目标 (Transfer Goal)

{transfer_goals}

## U: 持续理解 (Enduring Understandings)

学生将会理解......

{understandings}

### 大概念是什么？

{big_ideas}

### 期望他们获得的特定理解是什么？

{specific_understandings}

### 可预见的误区是什么？

{misconceptions}

## Q: 基本问题 (Essential Questions)

学生将不断思考......

{essential_questions}

## K: 学生应掌握的知识 (Knowledge)

作为本单元的学习结果，学生将会获得哪些关键知识？

{knowledge}

### 习得这些知识和技能后，他们最终能够做什么？

{knowledge_application}

## S: 学生应形成的技能 (Skills)

作为本单元的学习结果，学生将会获得哪些关键技能？

{skills}
"""


def get_stage_two_template() -> str:
    """
    获取阶段二模板：确定恰当的评估方法

    Returns:
        str: 阶段二的Markdown模板字符串
    """
    return """# 阶段二：确定恰当的评估方法

## 表现性任务

学生通过哪些**真实**的表现性任务证明自己已达到预期的理解目标？

{performance_tasks}

## 其他评估

学生通过哪些**其他证据**证明自己已达到了预期结果？

{other_assessments}

## 评估标准

{rubrics}
"""


def get_stage_three_template() -> str:
    """
    获取阶段三模板：规划学习体验和教学过程

    Returns:
        str: 阶段三的Markdown模板字符串
    """
    return """# 阶段三：规划学习体验和教学过程

## 学习活动 (基于 WHERETO 原则)

### W (Where & What): 确保学生了解所学单元的目标 (Where) 以及原因 (Why)

{whereto_w}

### H (Hook & Hold): 从一开始就吸引 (Hook) 并保持 (Hold) 他们的注意力

{whereto_h}

### E (Equip & Explore): 为学生提供必要的经验、工具、知识和技能来实现表现目标

{whereto_e}

### R (Rethink & Revise): 为学生提供大量机会来重新思考大概念，反思进展情况，并修改自己的设计工作

{whereto_r}

### E (Evaluate): 为学生评估进展和自我评估提供机会

{whereto_e2}

### T (Tailor): 量体裁衣，反映个人的天赋、兴趣、风格和需求

{whereto_t}

### O (Organize): 合理组织，以使学生获得深刻理解，而非肤浅了解

{whereto_o}

## 教学流程

### 前测

{pre_assessment}

### 贯穿整个项目的学习单 (脚手架)

{scaffolding}

## 项目阶段详细规划

{project_phases}
"""


def get_complete_template() -> str:
    """
    获取完整的三阶段UbD教案模板

    Returns:
        str: 完整的Markdown模板字符串
    """
    return f"""{get_stage_one_template()}

---

{get_stage_two_template()}

---

{get_stage_three_template()}
"""
