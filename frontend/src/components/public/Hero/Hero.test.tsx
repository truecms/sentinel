import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Hero } from './Hero'

describe('Hero', () => {
  const defaultProps = {
    title: 'Monitor Your Drupal Sites Security',
    subtitle: 'Real-time security monitoring and update tracking for all your Drupal sites',
    primaryButtonText: 'Get Started',
    secondaryButtonText: 'Learn More',
    onPrimaryClick: vi.fn(),
    onSecondaryClick: vi.fn(),
  }

  it('renders title and subtitle', () => {
    render(<Hero {...defaultProps} />)
    
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(defaultProps.title)
    expect(screen.getByText(defaultProps.subtitle)).toBeInTheDocument()
  })

  it('renders both CTA buttons', () => {
    render(<Hero {...defaultProps} />)
    
    expect(screen.getByRole('button', { name: defaultProps.primaryButtonText })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: defaultProps.secondaryButtonText })).toBeInTheDocument()
  })

  it('handles primary button click', async () => {
    render(<Hero {...defaultProps} />)
    
    const primaryButton = screen.getByRole('button', { name: defaultProps.primaryButtonText })
    await userEvent.click(primaryButton)
    
    expect(defaultProps.onPrimaryClick).toHaveBeenCalledTimes(1)
  })

  it('handles secondary button click', async () => {
    render(<Hero {...defaultProps} />)
    
    const secondaryButton = screen.getByRole('button', { name: defaultProps.secondaryButtonText })
    await userEvent.click(secondaryButton)
    
    expect(defaultProps.onSecondaryClick).toHaveBeenCalledTimes(1)
  })

  it('renders without secondary button when not provided', () => {
    const propsWithoutSecondary = {
      ...defaultProps,
      secondaryButtonText: undefined,
      onSecondaryClick: undefined,
    }
    
    render(<Hero {...propsWithoutSecondary} />)
    
    expect(screen.getByRole('button', { name: defaultProps.primaryButtonText })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: defaultProps.secondaryButtonText })).not.toBeInTheDocument()
  })

  it('renders background image when provided', () => {
    const backgroundImage = '/images/hero-bg.jpg'
    render(<Hero {...defaultProps} backgroundImage={backgroundImage} />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveStyle(`background-image: url(${backgroundImage})`)
  })

  it('renders hero image when provided', () => {
    const heroImage = {
      src: '/images/dashboard-preview.png',
      alt: 'Dashboard Preview'
    }
    
    render(<Hero {...defaultProps} image={heroImage} />)
    
    const img = screen.getByAltText(heroImage.alt)
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', heroImage.src)
  })

  it('applies dark variant styles', () => {
    render(<Hero {...defaultProps} variant="dark" />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveClass('bg-neutral-900', 'text-white')
  })

  it('applies centered alignment', () => {
    render(<Hero {...defaultProps} alignment="center" />)
    
    const contentContainer = screen.getByTestId('hero-content')
    expect(contentContainer).toHaveClass('text-center', 'mx-auto')
  })

  it('renders statistics when provided', () => {
    const statistics = [
      { label: 'Sites Monitored', value: '1000+' },
      { label: 'Security Issues Detected', value: '50K+' },
      { label: 'Uptime', value: '99.9%' },
    ]
    
    render(<Hero {...defaultProps} statistics={statistics} />)
    
    statistics.forEach(stat => {
      expect(screen.getByText(stat.label)).toBeInTheDocument()
      expect(screen.getByText(stat.value)).toBeInTheDocument()
    })
  })

  it('renders trust indicators', () => {
    const trustIndicators = ['SOC 2 Certified', 'GDPR Compliant', 'ISO 27001']
    
    render(<Hero {...defaultProps} trustIndicators={trustIndicators} />)
    
    trustIndicators.forEach(indicator => {
      expect(screen.getByText(indicator)).toBeInTheDocument()
    })
  })

  it('applies full height when specified', () => {
    render(<Hero {...defaultProps} fullHeight />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveClass('min-h-screen')
  })

  it('renders video background when provided', () => {
    const videoUrl = '/videos/hero-bg.mp4'
    
    render(<Hero {...defaultProps} videoBackground={videoUrl} />)
    
    const video = screen.getByTestId('hero-video')
    expect(video).toBeInTheDocument()
    expect(video).toHaveAttribute('src', videoUrl)
    expect(video).toHaveAttribute('autoplay')
    expect(video).toHaveAttribute('loop')
    expect(video).toHaveAttribute('muted')
  })

  it('applies gradient overlay with video background', () => {
    const videoUrl = '/videos/hero-bg.mp4'
    
    render(<Hero {...defaultProps} videoBackground={videoUrl} />)
    
    const overlay = screen.getByTestId('hero-overlay')
    expect(overlay).toHaveClass('bg-gradient-to-r', 'from-black/50', 'to-transparent')
  })

  it('renders animated elements', () => {
    render(<Hero {...defaultProps} animated />)
    
    const title = screen.getByRole('heading', { level: 1 })
    expect(title).toHaveAttribute('data-animate', 'fade-up')
  })

  it('supports custom className', () => {
    const customClass = 'custom-hero-class'
    
    render(<Hero {...defaultProps} className={customClass} />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveClass(customClass)
  })

  it('renders badge when provided', () => {
    const badge = {
      text: 'New',
      variant: 'success' as const
    }
    
    render(<Hero {...defaultProps} badge={badge} />)
    
    const badgeElement = screen.getByText(badge.text)
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('bg-success-100', 'text-success-800')
  })

  it('handles responsive image sizing', () => {
    const heroImage = {
      src: '/images/dashboard-preview.png',
      alt: 'Dashboard Preview',
      srcSet: '/images/dashboard-preview-sm.png 640w, /images/dashboard-preview-lg.png 1024w'
    }
    
    render(<Hero {...defaultProps} image={heroImage} />)
    
    const img = screen.getByAltText(heroImage.alt)
    expect(img).toHaveAttribute('srcset', heroImage.srcSet)
  })

  it('applies parallax effect when enabled', () => {
    render(<Hero {...defaultProps} parallax />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveAttribute('data-parallax', 'true')
  })

  it('renders social proof logos', () => {
    const logos = [
      { src: '/logos/company1.svg', alt: 'Company 1' },
      { src: '/logos/company2.svg', alt: 'Company 2' },
    ]
    
    render(<Hero {...defaultProps} socialProofLogos={logos} />)
    
    logos.forEach(logo => {
      const img = screen.getByAltText(logo.alt)
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src', logo.src)
    })
  })

  it('supports icon for primary button', () => {
    const ArrowIcon = () => <svg data-testid="arrow-icon" />
    
    render(<Hero {...defaultProps} primaryButtonIcon={ArrowIcon} />)
    
    expect(screen.getByTestId('arrow-icon')).toBeInTheDocument()
  })

  it('renders countdown timer when provided', () => {
    const countdownDate = new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours from now
    
    render(<Hero {...defaultProps} countdownTo={countdownDate} />)
    
    expect(screen.getByTestId('countdown-timer')).toBeInTheDocument()
    expect(screen.getByText(/hours/i)).toBeInTheDocument()
    expect(screen.getByText(/minutes/i)).toBeInTheDocument()
  })

  it('handles scroll indicator click', async () => {
    render(<Hero {...defaultProps} showScrollIndicator />)
    
    const scrollIndicator = screen.getByLabelText('Scroll down')
    const scrollIntoViewMock = vi.fn()
    
    // Mock the next section
    const nextSection = document.createElement('div')
    nextSection.id = 'next-section'
    document.body.appendChild(nextSection)
    nextSection.scrollIntoView = scrollIntoViewMock
    
    await userEvent.click(scrollIndicator)
    
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' })
    
    document.body.removeChild(nextSection)
  })

  it('applies correct spacing for different sizes', () => {
    const { rerender } = render(<Hero {...defaultProps} size="small" />)
    
    const heroSection = screen.getByTestId('hero-section')
    expect(heroSection).toHaveClass('py-12')
    
    rerender(<Hero {...defaultProps} size="medium" />)
    expect(heroSection).toHaveClass('py-20')
    
    rerender(<Hero {...defaultProps} size="large" />)
    expect(heroSection).toHaveClass('py-32')
  })

  it('handles keyboard navigation for buttons', async () => {
    render(<Hero {...defaultProps} />)
    
    const primaryButton = screen.getByRole('button', { name: defaultProps.primaryButtonText })
    const secondaryButton = screen.getByRole('button', { name: defaultProps.secondaryButtonText })
    
    primaryButton.focus()
    expect(document.activeElement).toBe(primaryButton)
    
    fireEvent.keyDown(primaryButton, { key: 'Tab' })
    expect(document.activeElement).toBe(secondaryButton)
  })

  it('supports RTL layout', () => {
    render(<Hero {...defaultProps} rtl />)
    
    const heroContent = screen.getByTestId('hero-content')
    expect(heroContent).toHaveAttribute('dir', 'rtl')
  })

  it('renders announcement bar when provided', () => {
    const announcement = {
      text: 'Limited time offer: 20% off all plans',
      link: '/pricing',
      linkText: 'View pricing'
    }
    
    render(<Hero {...defaultProps} announcement={announcement} />)
    
    expect(screen.getByText(announcement.text)).toBeInTheDocument()
    const link = screen.getByText(announcement.linkText)
    expect(link).toHaveAttribute('href', announcement.link)
  })
})