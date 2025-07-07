import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Shield } from 'lucide-react'
import { FeatureCard } from './FeatureCard'

describe('FeatureCard', () => {
  const defaultProps = {
    title: 'Real-time Monitoring',
    description: 'Monitor your Drupal sites in real-time with instant alerts',
    icon: Shield,
  }

  it('renders title and description', () => {
    render(<FeatureCard {...defaultProps} />)
    
    expect(screen.getByText(defaultProps.title)).toBeInTheDocument()
    expect(screen.getByText(defaultProps.description)).toBeInTheDocument()
  })

  it('renders icon', () => {
    render(<FeatureCard {...defaultProps} />)
    
    const icon = screen.getByTestId('feature-icon')
    expect(icon).toBeInTheDocument()
    expect(icon.querySelector('svg')).toBeInTheDocument()
  })

  it('handles click event', async () => {
    const handleClick = vi.fn()
    render(<FeatureCard {...defaultProps} onClick={handleClick} />)
    
    const card = screen.getByTestId('feature-card')
    await userEvent.click(card)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('shows hover state when clickable', async () => {
    const handleClick = vi.fn()
    render(<FeatureCard {...defaultProps} onClick={handleClick} />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass('cursor-pointer', 'hover:shadow-lg')
  })

  it('renders with link', () => {
    const href = '/features/monitoring'
    render(<FeatureCard {...defaultProps} href={href} />)
    
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', href)
  })

  it('renders badge when provided', () => {
    const badge = { text: 'New', variant: 'primary' as const }
    render(<FeatureCard {...defaultProps} badge={badge} />)
    
    const badgeElement = screen.getByText(badge.text)
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('bg-primary-100', 'text-primary-800')
  })

  it('renders list items when provided', () => {
    const items = [
      'Track all modules',
      'Security updates',
      'Version comparison',
    ]
    
    render(<FeatureCard {...defaultProps} items={items} />)
    
    items.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument()
    })
    
    const checkmarks = screen.getAllByTestId('checkmark-icon')
    expect(checkmarks).toHaveLength(items.length)
  })

  it('renders learn more link', () => {
    const learnMoreLink = '/learn-more'
    const learnMoreText = 'Learn more'
    
    render(
      <FeatureCard 
        {...defaultProps} 
        learnMoreLink={learnMoreLink}
        learnMoreText={learnMoreText}
      />
    )
    
    const link = screen.getByText(learnMoreText)
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', learnMoreLink)
  })

  it('applies highlighted variant', () => {
    render(<FeatureCard {...defaultProps} variant="highlighted" />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass('border-primary-500', 'shadow-lg')
  })

  it('applies compact size', () => {
    render(<FeatureCard {...defaultProps} size="compact" />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass('p-4')
    
    const title = screen.getByText(defaultProps.title)
    expect(title).toHaveClass('text-lg')
  })

  it('applies large size', () => {
    render(<FeatureCard {...defaultProps} size="large" />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass('p-8')
    
    const title = screen.getByText(defaultProps.title)
    expect(title).toHaveClass('text-2xl')
  })

  it('renders image when provided', () => {
    const image = {
      src: '/images/feature-preview.png',
      alt: 'Feature preview'
    }
    
    render(<FeatureCard {...defaultProps} image={image} />)
    
    const img = screen.getByAltText(image.alt)
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', image.src)
  })

  it('applies color variants', () => {
    const { rerender } = render(<FeatureCard {...defaultProps} color="primary" />)
    
    const iconContainer = screen.getByTestId('feature-icon')
    expect(iconContainer).toHaveClass('bg-primary-100', 'text-primary-600')
    
    rerender(<FeatureCard {...defaultProps} color="success" />)
    expect(iconContainer).toHaveClass('bg-success-100', 'text-success-600')
    
    rerender(<FeatureCard {...defaultProps} color="warning" />)
    expect(iconContainer).toHaveClass('bg-warning-100', 'text-warning-600')
  })

  it('shows coming soon state', () => {
    render(<FeatureCard {...defaultProps} comingSoon />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass('opacity-75')
    
    expect(screen.getByText('Coming Soon')).toBeInTheDocument()
  })

  it('disables interaction when coming soon', async () => {
    const handleClick = vi.fn()
    render(<FeatureCard {...defaultProps} comingSoon onClick={handleClick} />)
    
    const card = screen.getByTestId('feature-card')
    await userEvent.click(card)
    
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders statistics when provided', () => {
    const stats = {
      value: '99.9%',
      label: 'Uptime'
    }
    
    render(<FeatureCard {...defaultProps} stats={stats} />)
    
    expect(screen.getByText(stats.value)).toBeInTheDocument()
    expect(screen.getByText(stats.label)).toBeInTheDocument()
  })

  it('applies animation on hover', async () => {
    render(<FeatureCard {...defaultProps} animated />)
    
    const card = screen.getByTestId('feature-card')
    
    fireEvent.mouseEnter(card)
    expect(card).toHaveClass('transform', 'scale-105')
    
    fireEvent.mouseLeave(card)
    expect(card).not.toHaveClass('scale-105')
  })

  it('renders category label', () => {
    const category = 'Security'
    render(<FeatureCard {...defaultProps} category={category} />)
    
    expect(screen.getByText(category)).toBeInTheDocument()
  })

  it('supports custom className', () => {
    const customClass = 'custom-feature-card'
    render(<FeatureCard {...defaultProps} className={customClass} />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveClass(customClass)
  })

  it('renders action button when provided', () => {
    const action = {
      text: 'Try Now',
      onClick: vi.fn()
    }
    
    render(<FeatureCard {...defaultProps} action={action} />)
    
    const button = screen.getByText(action.text)
    expect(button).toBeInTheDocument()
  })

  it('handles action button click', async () => {
    const action = {
      text: 'Try Now',
      onClick: vi.fn()
    }
    
    render(<FeatureCard {...defaultProps} action={action} />)
    
    const button = screen.getByText(action.text)
    await userEvent.click(button)
    
    expect(action.onClick).toHaveBeenCalledTimes(1)
  })

  it('stops propagation on action button click', async () => {
    const handleCardClick = vi.fn()
    const handleActionClick = vi.fn()
    
    const action = {
      text: 'Try Now',
      onClick: handleActionClick
    }
    
    render(<FeatureCard {...defaultProps} onClick={handleCardClick} action={action} />)
    
    const button = screen.getByText(action.text)
    await userEvent.click(button)
    
    expect(handleActionClick).toHaveBeenCalledTimes(1)
    expect(handleCardClick).not.toHaveBeenCalled()
  })

  it('renders with grid layout', () => {
    render(<FeatureCard {...defaultProps} layout="grid" />)
    
    const content = screen.getByTestId('feature-content')
    expect(content).toHaveClass('grid', 'md:grid-cols-2')
  })

  it('shows new indicator for recent features', () => {
    const releaseDate = new Date()
    releaseDate.setDate(releaseDate.getDate() - 7) // 7 days ago
    
    render(<FeatureCard {...defaultProps} releaseDate={releaseDate} />)
    
    expect(screen.getByText('New')).toBeInTheDocument()
  })

  it('does not show new indicator for old features', () => {
    const releaseDate = new Date()
    releaseDate.setDate(releaseDate.getDate() - 31) // 31 days ago
    
    render(<FeatureCard {...defaultProps} releaseDate={releaseDate} />)
    
    expect(screen.queryByText('New')).not.toBeInTheDocument()
  })

  it('renders testimonial quote when provided', () => {
    const testimonial = {
      quote: 'This feature saved us hours of work',
      author: 'John Doe',
      company: 'ACME Corp'
    }
    
    render(<FeatureCard {...defaultProps} testimonial={testimonial} />)
    
    expect(screen.getByText(`"${testimonial.quote}"`)).toBeInTheDocument()
    expect(screen.getByText(`- ${testimonial.author}, ${testimonial.company}`)).toBeInTheDocument()
  })

  it('handles keyboard navigation', async () => {
    const handleClick = vi.fn()
    render(<FeatureCard {...defaultProps} onClick={handleClick} />)
    
    const card = screen.getByTestId('feature-card')
    card.focus()
    
    fireEvent.keyDown(card, { key: 'Enter' })
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    fireEvent.keyDown(card, { key: ' ' })
    expect(handleClick).toHaveBeenCalledTimes(2)
  })

  it('has proper ARIA attributes for clickable cards', () => {
    const handleClick = vi.fn()
    render(<FeatureCard {...defaultProps} onClick={handleClick} />)
    
    const card = screen.getByTestId('feature-card')
    expect(card).toHaveAttribute('role', 'button')
    expect(card).toHaveAttribute('tabIndex', '0')
  })

  it('renders video preview when provided', () => {
    const video = {
      src: '/videos/feature-demo.mp4',
      poster: '/images/video-poster.jpg'
    }
    
    render(<FeatureCard {...defaultProps} video={video} />)
    
    const videoElement = screen.getByTestId('feature-video')
    expect(videoElement).toHaveAttribute('src', video.src)
    expect(videoElement).toHaveAttribute('poster', video.poster)
  })
})