import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TimelineChart } from './TimelineChart'
import type { TimeSeriesData } from '../../../../types/dashboard'

// Mock Recharts to avoid canvas rendering issues in tests
vi.mock('recharts', () => ({
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  AreaChart: ({ children }: { children: React.ReactNode }) => <div data-testid="area-chart">{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Line: () => null,
  Area: () => null,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  ReferenceLine: () => null,
}))

describe('TimelineChart', () => {
  const mockData: TimeSeriesData[] = [
    {
      timestamp: new Date('2024-01-01T10:00:00'),
      value: 100,
      label: 'security',
    },
    {
      timestamp: new Date('2024-01-01T11:00:00'),
      value: 120,
      label: 'security',
    },
    {
      timestamp: new Date('2024-01-01T12:00:00'),
      value: 110,
      label: 'security',
    },
    {
      timestamp: new Date('2024-01-01T10:00:00'),
      value: 50,
      label: 'updates',
    },
    {
      timestamp: new Date('2024-01-01T11:00:00'),
      value: 60,
      label: 'updates',
    },
    {
      timestamp: new Date('2024-01-01T12:00:00'),
      value: 55,
      label: 'updates',
    },
  ]

  it('renders line chart by default', () => {
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={['security', 'updates']}
      />
    )
    
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('renders area chart when type is area', () => {
    render(
      <TimelineChart
        data={mockData}
        type="area"
        period="hour"
        metrics={['security', 'updates']}
      />
    )
    
    expect(screen.getByTestId('area-chart')).toBeInTheDocument()
  })

  it('renders bar chart when type is bar', () => {
    render(
      <TimelineChart
        data={mockData}
        type="bar"
        period="hour"
        metrics={['security', 'updates']}
      />
    )
    
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    const { container } = render(
      <TimelineChart
        data={[]}
        period="hour"
        metrics={[]}
        loading={true}
        height={300}
      />
    )
    
    const loadingElement = container.querySelector('.animate-pulse')
    expect(loadingElement).toBeInTheDocument()
    expect(loadingElement).toHaveStyle({ height: '300px' })
  })

  it('shows empty state when no data', () => {
    render(
      <TimelineChart
        data={[]}
        period="hour"
        metrics={[]}
      />
    )
    
    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('renders legend for multiple metrics', () => {
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={['security', 'updates']}
      />
    )
    
    expect(screen.getByText('security')).toBeInTheDocument()
    expect(screen.getByText('updates')).toBeInTheDocument()
  })

  it('does not render legend for single metric', () => {
    const singleMetricData: TimeSeriesData[] = [
      {
        timestamp: new Date('2024-01-01T10:00:00'),
        value: 100,
      },
    ]
    
    render(
      <TimelineChart
        data={singleMetricData}
        period="hour"
        metrics={['value']}
      />
    )
    
    // Legend should not be present for single metric
    const legend = screen.queryByText('value')
    expect(legend).not.toBeInTheDocument()
  })

  it('handles custom height', () => {
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={['security']}
        height={400}
      />
    )
    
    const responsiveContainer = screen.getByTestId('responsive-container')
    expect(responsiveContainer.parentElement).toBeTruthy()
  })

  it('auto-detects metrics when not provided', () => {
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={[]}
      />
    )
    
    // Should auto-detect both metrics from data
    expect(screen.getByText('security')).toBeInTheDocument()
    expect(screen.getByText('updates')).toBeInTheDocument()
  })

  it('handles data without labels', () => {
    const unlabeledData: TimeSeriesData[] = [
      {
        timestamp: new Date('2024-01-01T10:00:00'),
        value: 100,
      },
      {
        timestamp: new Date('2024-01-01T11:00:00'),
        value: 120,
      },
    ]
    
    render(
      <TimelineChart
        data={unlabeledData}
        period="hour"
        metrics={[]}
      />
    )
    
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
  })

  it('renders with annotations', () => {
    const annotations = [
      {
        timestamp: new Date('2024-01-01T11:00:00'),
        label: 'Security Alert',
        color: '#ef4444',
      },
    ]
    
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={['security']}
        annotations={annotations}
      />
    )
    
    // Chart should still render with annotations
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
  })

  it('renders without interactivity when disabled', () => {
    render(
      <TimelineChart
        data={mockData}
        period="hour"
        metrics={['security']}
        interactive={false}
      />
    )
    
    // Chart should still render
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
  })
})