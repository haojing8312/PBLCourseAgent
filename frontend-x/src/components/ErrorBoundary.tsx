/**
 * ErrorBoundary - React错误边界组件
 * 捕获子组件中的JavaScript错误并显示友好的错误界面
 */

import React, { Component, ReactNode } from 'react';
import { Result, Button } from 'antd';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary组件
 *
 * 捕获组件树中的错误，防止整个应用崩溃
 *
 * @example
 * ```tsx
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <Result
            status="error"
            title="应用出现错误"
            subTitle="抱歉，应用遇到了一个错误。请尝试刷新页面。"
            extra={
              <Button type="primary" onClick={this.handleReset}>
                刷新页面
              </Button>
            }
          >
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={{ textAlign: 'left', marginTop: 20 }}>
                <summary>错误详情</summary>
                <pre style={{ marginTop: 10, padding: 10, background: '#f5f5f5', borderRadius: 4 }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
