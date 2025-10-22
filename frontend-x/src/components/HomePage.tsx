/**
 * HomePage.tsx - UbD-PBL课程架构师首页
 * 设计方案：渐变流体设计（国际顶级水准）
 *
 * 设计特点：
 * - 紫蓝渐变主题
 * - 玻璃态效果（glassmorphism）
 * - 流体背景动画
 * - 现代化交互和排版
 */

import React, { useEffect, useRef } from 'react';
import { Button } from 'antd';
import {
  ArrowRightOutlined,
  CheckCircleFilled,
  BulbFilled,
  ThunderboltFilled,
  ClockCircleFilled,
} from '@ant-design/icons';
import './HomePage.css';

interface HomePageProps {
  onStartClick: () => void;
  onHelpClick: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onStartClick, onHelpClick }) => {
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);

  // 滚动揭示动画
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
          }
        });
      },
      { threshold: 0.1 }
    );

    sectionRefs.current.forEach((ref) => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className="homepage-container">
      {/* 背景装饰层 */}
      <div className="hero-background">
        <div className="gradient-blob blob-1" />
        <div className="gradient-blob blob-2" />
        <div className="gradient-blob blob-3" />
        <div className="grid-pattern" />
      </div>

      {/* Hero区域 */}
      <section className="hero-section">
        <h1 className="hero-title">
          <span className="gradient-text">AI驱动</span>的
          <br />
          PBL课程设计助手
        </h1>

        <p className="hero-subtitle">
          基于UbD理念，30分钟完成传统需90分钟的课程设计
          <br />
          从课程目标到学习蓝图，一站式智能生成
        </p>

        <button className="cta-button-primary" onClick={onStartClick}>
          开始UBD教研
          <ArrowRightOutlined />
        </button>

        <div className="trust-indicators">
          <div className="trust-indicator-item">
            <CheckCircleFilled className="trust-indicator-icon" />
            <span>基于UbD理念</span>
          </div>
          <div className="trust-indicator-item">
            <CheckCircleFilled className="trust-indicator-icon" />
            <span>三阶段智能生成</span>
          </div>
          <div className="trust-indicator-item">
            <CheckCircleFilled className="trust-indicator-icon" />
            <span>即导即用</span>
          </div>
        </div>
      </section>

      {/* 核心功能区域 */}
      <section
        className="features-section scroll-reveal"
        ref={(el) => (sectionRefs.current[0] = el)}
      >
        <div className="features-grid">
          {/* 功能卡片 1 */}
          <div className="glass-card">
            <BulbFilled className="card-icon" />
            <h3 className="card-title">符合UbD理念</h3>
            <p className="card-description">
              基于"理解优先设计"（Understanding by Design）理念，确保学习目标、评估方式和教学活动三者完美对齐，让课程设计更科学、更有深度。
            </p>
          </div>

          {/* 功能卡片 2 */}
          <div className="glass-card">
            <ThunderboltFilled className="card-icon" />
            <h3 className="card-title">AI自动生成</h3>
            <p className="card-description">
              智能生成三阶段完整方案：项目基础定义、评估框架设计、完整学习蓝图。AI理解教育原理，输出专业级课程文档，质量媲美资深教研专家。
            </p>
          </div>

          {/* 功能卡片 3 */}
          <div className="glass-card">
            <ClockCircleFilled className="card-icon" />
            <h3 className="card-title">节省教研时间</h3>
            <p className="card-description">
              传统课程设计需要90分钟以上，现在只需30分钟即可完成初稿。更多时间用于优化细节和个性化调整，让教师专注于创造性工作。
            </p>
          </div>
        </div>
      </section>

      {/* 使用流程区域 */}
      <section
        className="process-section scroll-reveal"
        ref={(el) => (sectionRefs.current[1] = el)}
      >
        <div className="process-container">
          <h2 className="section-title">三步完成课程设计</h2>

          <div className="process-steps">
            {/* 步骤 1 */}
            <div className="process-step">
              <div className="step-number">1</div>
              <h4 className="step-title">填写课程信息</h4>
              <p className="step-description">
                输入课程主题、学习对象、课程目标等基本信息，系统会智能理解您的教学意图
              </p>
            </div>

            {/* 步骤 2 */}
            <div className="process-step">
              <div className="step-number">2</div>
              <h4 className="step-title">AI生成方案</h4>
              <p className="step-description">
                AI自动生成三阶段完整设计：项目基础、评估框架、学习蓝图，符合UbD逆向设计原则
              </p>
            </div>

            {/* 步骤 3 */}
            <div className="process-step">
              <div className="step-number">3</div>
              <h4 className="step-title">导出使用</h4>
              <p className="step-description">
                一键导出Markdown格式文档，或继续通过AI对话优化方案，直至完美
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 底部CTA区域 */}
      <section
        className="bottom-cta scroll-reveal"
        ref={(el) => (sectionRefs.current[2] = el)}
      >
        <h2 className="bottom-cta-title">准备好开始了吗？</h2>
        <button className="cta-button-primary" onClick={onStartClick}>
          开始UBD教研
          <ArrowRightOutlined />
        </button>
      </section>

      {/* 页脚 */}
      <footer className="homepage-footer">
        <div className="footer-links">
          <span
            className="footer-link"
            onClick={onHelpClick}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => e.key === 'Enter' && onHelpClick()}
          >
            帮助文档
          </span>
          <span className="footer-divider">|</span>
          <span style={{ color: 'var(--text-tertiary)' }}>
            v3.0 Markdown架构
          </span>
        </div>
      </footer>
    </div>
  );
};
