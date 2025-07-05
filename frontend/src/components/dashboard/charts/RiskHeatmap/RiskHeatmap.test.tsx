import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { RiskHeatmap } from './RiskHeatmap'
import type { RiskData } from '../../../../types/dashboard'

describe('RiskHeatmap', () => {
  const mockData: RiskData[][] = [
    [
      { value: 85, label: 'Critical Issue', severity: 'critical' },
      { value: 60, label: 'High Risk', severity: 'high' },
      { value: 30, label: 'Medium Risk', severity: 'medium' },
    ],
    [
      { value: 45, label: 'Medium Risk', severity: 'medium' },
      { value: 20, label: 'Low Risk', severity: 'low' },
      { value: 10, label: 'Info', severity: 'info' },
    ],
    [
      { value: 75, label: 'High Risk', severity: 'high' },
      { value: 50, label: 'Medium Risk', severity: 'medium' },
      undefined, // empty cell
    ],
  ]
  
  const xAxis = ['Site A', 'Site B', 'Site C']
  const yAxis = ['Module 1', 'Module 2', 'Module 3']
  
  it('renders heatmap grid correctly', () => {
    render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
      />
    )
    
    // Check x-axis labels
    xAxis.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
    
    // Check y-axis labels
    yAxis.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
    
    // Check cell values
    expect(screen.getByText('85')).toBeInTheDocument()
    expect(screen.getByText('60')).toBeInTheDocument()
    expect(screen.getByText('30')).toBeInTheDocument()
  })
  
  it('handles cell clicks', () => {
    const handleCellClick = vi.fn()
    
    render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
        onCellClick={handleCellClick}
      />
    )
    
    // Click on first cell with value 85
    fireEvent.click(screen.getByText('85'))
    expect(handleCellClick).toHaveBeenCalledWith(0, 0)
    
    // Click on cell with value 20
    fireEvent.click(screen.getByText('20'))
    expect(handleCellClick).toHaveBeenCalledWith(1, 1)
  })
  
  it('shows loading state', () => {
    const { container } = render(
      <RiskHeatmap
        data={[]}
        xAxis={xAxis}
        yAxis={yAxis}
        loading={true}
      />
    )
    
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })
  
  it('renders empty cells correctly', () => {
    const { container } = render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
      />
    )
    
    // Should have total cells = xAxis.length * yAxis.length
    const totalCells = xAxis.length * yAxis.length
    
    // Count cells with motion divs that have background color style
    const dataCells = container.querySelectorAll('.cursor-pointer')
    
    expect(dataCells).toHaveLength(totalCells)
  })
  
  it('applies custom color scale', () => {
    const customColorScale = {
      min: '#00ff00',
      max: '#ff0000',
      steps: ['#00ff00', '#ffff00', '#ff0000'],
    }
    
    const { container } = render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
        colorScale={customColorScale}
      />
    )
    
    // Should apply custom colors based on value
    const cells = container.querySelectorAll('.cursor-pointer')
    expect(cells.length).toBeGreaterThan(0)
  })
  
  it('shows tooltip on hover when provided', async () => {
    const tooltipFn = vi.fn((data: RiskData) => (
      <div>Tooltip: {data.label}</div>
    ))
    
    render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
        tooltip={tooltipFn}
      />
    )
    
    // Hover over a cell
    const cell = screen.getByText('85')
    fireEvent.mouseEnter(cell.parentElement!)
    
    // Tooltip function should be called
    expect(tooltipFn).toHaveBeenCalled()
  })
  
  it('renders legend correctly', () => {
    render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
      />
    )
    
    expect(screen.getByText('Risk Level:')).toBeInTheDocument()
    expect(screen.getByText('critical')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
    expect(screen.getByText('low')).toBeInTheDocument()
    expect(screen.getByText('info')).toBeInTheDocument()
  })
  
  it('handles hover state correctly', () => {
    render(
      <RiskHeatmap
        data={mockData}
        xAxis={xAxis}
        yAxis={yAxis}
      />
    )
    
    const cell = screen.getByText('85').parentElement!
    
    // Mouse enter
    fireEvent.mouseEnter(cell)
    expect(cell).toHaveClass('ring-2')
    
    // Mouse leave
    fireEvent.mouseLeave(cell)
    expect(cell).not.toHaveClass('ring-2')
  })
  
  it('handles empty data array', () => {
    const emptyData: RiskData[][] = [
      [undefined, undefined],
      [undefined, undefined],
    ]
    
    const { container } = render(
      <RiskHeatmap
        data={emptyData}
        xAxis={['A', 'B']}
        yAxis={['1', '2']}
      />
    )
    
    // Should still render grid structure
    expect(screen.getByText('A')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    
    // All cells should be rendered
    const cells = container.querySelectorAll('.cursor-pointer')
    expect(cells.length).toBe(4) // 2x2 grid
  })
  
  it('adjusts cell size based on grid dimensions', () => {
    const largeXAxis = Array.from({ length: 20 }, (_, i) => `X${i}`)
    const largeYAxis = Array.from({ length: 20 }, (_, i) => `Y${i}`)
    const largeData = Array(20).fill(Array(20).fill({ value: 50, label: 'Test', severity: 'medium' as const }))
    
    const { container } = render(
      <RiskHeatmap
        data={largeData}
        xAxis={largeXAxis}
        yAxis={largeYAxis}
      />
    )
    
    // Should render with adjusted cell sizes
    const cells = container.querySelectorAll('[style*="width:"][style*="height:"]')
    expect(cells.length).toBeGreaterThan(0)
  })
})