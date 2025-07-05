import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SecurityGauge } from './SecurityGauge'

describe('SecurityGauge', () => {
  const defaultThresholds = {
    critical: 30,
    warning: 60,
    good: 80,
  }

  it('displays score and label correctly', () => {
    render(
      <SecurityGauge
        score={75}
        label="Security Score"
        thresholds={defaultThresholds}
      />
    )
    
    expect(screen.getByText('75%')).toBeInTheDocument()
    expect(screen.getByText('Security Score')).toBeInTheDocument()
  })

  it('normalizes scores outside 0-100 range', () => {
    const { rerender } = render(
      <SecurityGauge
        score={150}
        label="Over 100"
        thresholds={defaultThresholds}
      />
    )
    
    expect(screen.getByText('100%')).toBeInTheDocument()
    
    rerender(
      <SecurityGauge
        score={-50}
        label="Below 0"
        thresholds={defaultThresholds}
      />
    )
    
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  it('renders different sizes correctly', () => {
    const sizes = ['small', 'medium', 'large'] as const
    
    sizes.forEach(size => {
      const { container } = render(
        <SecurityGauge
          key={size}
          score={50}
          label={`${size} gauge`}
          thresholds={defaultThresholds}
          size={size}
        />
      )
      
      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
      
      // Check that SVG has appropriate dimensions
      const width = parseInt(svg!.getAttribute('width') || '0')
      expect(width).toBeGreaterThan(0)
    })
  })

  it('renders without animation when animated is false', () => {
    const { container } = render(
      <SecurityGauge
        score={85}
        label="No Animation"
        thresholds={defaultThresholds}
        animated={false}
      />
    )
    
    const paths = container.querySelectorAll('path')
    // Should have background and score paths
    expect(paths.length).toBeGreaterThanOrEqual(2)
  })

  it('applies correct colors based on thresholds', () => {
    const { container, rerender } = render(
      <SecurityGauge
        score={90}
        label="Good Score"
        thresholds={defaultThresholds}
      />
    )
    
    // Good score (>= 80) should use success color
    let scorePath = container.querySelectorAll('path')[1]
    expect(scorePath.getAttribute('stroke')).toBe('#10b981')
    
    // Warning score (>= 60, < 80)
    rerender(
      <SecurityGauge
        score={70}
        label="Warning Score"
        thresholds={defaultThresholds}
      />
    )
    
    scorePath = container.querySelectorAll('path')[1]
    expect(scorePath.getAttribute('stroke')).toBe('#f59e0b')
    
    // Critical score (< 60)
    rerender(
      <SecurityGauge
        score={25}
        label="Critical Score"
        thresholds={defaultThresholds}
      />
    )
    
    scorePath = container.querySelectorAll('path')[1]
    expect(scorePath.getAttribute('stroke')).toBe('#ef4444')
  })

  it('renders threshold markers', () => {
    const { container } = render(
      <SecurityGauge
        score={50}
        label="With Markers"
        thresholds={defaultThresholds}
      />
    )
    
    const lines = container.querySelectorAll('line')
    // Should have 3 threshold markers
    expect(lines).toHaveLength(3)
  })

  it('handles edge case scores correctly', () => {
    const { rerender } = render(
      <SecurityGauge
        score={0}
        label="Zero Score"
        thresholds={defaultThresholds}
      />
    )
    
    expect(screen.getByText('0%')).toBeInTheDocument()
    
    rerender(
      <SecurityGauge
        score={100}
        label="Perfect Score"
        thresholds={defaultThresholds}
      />
    )
    
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  it('applies correct text size classes for different sizes', () => {
    const { container } = render(
      <SecurityGauge
        score={75}
        label="Large Text"
        thresholds={defaultThresholds}
        size="large"
      />
    )
    
    const scoreElement = screen.getByText('75%')
    expect(scoreElement).toHaveClass('text-3xl')
    
    const labelElement = screen.getByText('Large Text')
    expect(labelElement).toHaveClass('text-base')
  })
})