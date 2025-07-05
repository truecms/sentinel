import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Shield } from 'lucide-react'
import { MetricCard } from './MetricCard'

describe('MetricCard', () => {
  it('displays title and value correctly', () => {
    render(
      <MetricCard title="Security Updates" value={23} />
    )
    
    expect(screen.getByText('Security Updates')).toBeInTheDocument()
    expect(screen.getByText('23')).toBeInTheDocument()
  })

  it('shows change indicator when provided', () => {
    render(
      <MetricCard
        title="Security Updates"
        value={23}
        change={{ value: 15, type: 'increase', period: '7d' }}
      />
    )
    
    expect(screen.getByText('+15%')).toBeInTheDocument()
    expect(screen.getByText('7d')).toBeInTheDocument()
  })

  it('applies correct color classes', () => {
    const { container } = render(
      <MetricCard
        title="Critical Issues"
        value={5}
        color="danger"
        icon={Shield}
      />
    )
    
    const iconContainer = container.querySelector('.bg-red-50')
    expect(iconContainer).toBeInTheDocument()
    expect(iconContainer).toHaveClass('text-red-600', 'border-red-200')
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    
    render(
      <MetricCard
        title="Test Card"
        value={10}
        onClick={handleClick}
      />
    )
    
    const card = screen.getByText('Test Card').closest('div[class*="cursor-pointer"]')
    expect(card).toBeInTheDocument()
    
    fireEvent.click(card!)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows loading state', () => {
    const { container } = render(
      <MetricCard
        title="Loading Card"
        value={0}
        loading={true}
      />
    )
    
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
    expect(screen.queryByText('0')).not.toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    const { container } = render(
      <MetricCard
        title="With Icon"
        value={42}
        icon={Shield}
      />
    )
    
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveClass('w-6', 'h-6')
  })

  it('shows decrease indicator correctly', () => {
    render(
      <MetricCard
        title="Decreased Metric"
        value={10}
        change={{ value: -5, type: 'decrease', period: '30d' }}
      />
    )
    
    expect(screen.getByText('-5%')).toBeInTheDocument()
    const changeContainer = screen.getByText('-5%').parentElement
    expect(changeContainer).toHaveClass('text-red-600')
  })

  it('does not show change indicator when loading', () => {
    render(
      <MetricCard
        title="Loading with Change"
        value={10}
        change={{ value: 15, type: 'increase', period: '7d' }}
        loading={true}
      />
    )
    
    expect(screen.queryByText('+15%')).not.toBeInTheDocument()
  })

  it('renders string values correctly', () => {
    render(
      <MetricCard
        title="String Value"
        value="99.9%"
      />
    )
    
    expect(screen.getByText('99.9%')).toBeInTheDocument()
  })

  it('applies all color variants correctly', () => {
    const colors = ['success', 'warning', 'danger', 'info'] as const
    const expectedClasses = {
      success: 'bg-green-50',
      warning: 'bg-amber-50',
      danger: 'bg-red-50',
      info: 'bg-blue-50',
    }
    
    colors.forEach(color => {
      const { container } = render(
        <MetricCard
          key={color}
          title={`${color} Card`}
          value={1}
          color={color}
          icon={Shield}
        />
      )
      
      const iconContainer = container.querySelector(`.${expectedClasses[color]}`)
      expect(iconContainer).toBeInTheDocument()
    })
  })
})