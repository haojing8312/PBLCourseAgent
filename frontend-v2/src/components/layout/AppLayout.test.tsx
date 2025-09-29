import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AppLayout } from './AppLayout'

// Mock Zustand store
vi.mock('@/stores/appStore', () => ({
  useAppStore: () => ({
    chatOpen: false,
  })
}))

// Mock child components
vi.mock('@/components/canvas/InfiniteCanvas', () => ({
  InfiniteCanvas: () => <div data-testid="infinite-canvas">Canvas</div>
}))

vi.mock('@/components/chat/ChatSidebar', () => ({
  ChatSidebar: () => <div data-testid="chat-sidebar">Chat Sidebar</div>
}))

vi.mock('@/components/ui/Toolbar', () => ({
  Toolbar: () => <div data-testid="toolbar">Toolbar</div>
}))

vi.mock('@/components/ui/StatusBar', () => ({
  StatusBar: () => <div data-testid="status-bar">Status Bar</div>
}))

describe('AppLayout', () => {
  it('renders main layout components', () => {
    render(<AppLayout />)

    expect(screen.getByTestId('toolbar')).toBeInTheDocument()
    expect(screen.getByTestId('infinite-canvas')).toBeInTheDocument()
    expect(screen.getByTestId('status-bar')).toBeInTheDocument()
  })
})