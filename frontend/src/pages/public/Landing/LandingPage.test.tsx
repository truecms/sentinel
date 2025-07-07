import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { LandingPage } from './LandingPage'

// Mock components
vi.mock('../../../components/public/Hero/Hero', () => ({
  Hero: ({ onCtaClick }: { onCtaClick: () => void }) => (
    <div data-testid="hero">
      <button onClick={onCtaClick}>Get Started</button>
    </div>
  )
}))

vi.mock('../../../components/public/FeatureCard/FeatureCard', () => ({
  FeatureCard: ({ title }: { title: string }) => (
    <div data-testid="feature-card">{title}</div>
  )
}))

vi.mock('../../../components/public/Testimonial/Testimonial', () => ({
  Testimonial: ({ author }: { author: string }) => (
    <div data-testid="testimonial">{author}</div>
  )
}))

vi.mock('../../../components/public/FAQ/FAQ', () => ({
  FAQ: () => <div data-testid="faq">FAQ Section</div>
}))

vi.mock('../../../components/public/CTA/CTA', () => ({
  CTA: () => <div data-testid="cta">CTA Section</div>
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

describe('LandingPage', () => {
  const renderWithProviders = () => {
    return render(
      <HelmetProvider>
        <MemoryRouter>
          <LandingPage />
        </MemoryRouter>
      </HelmetProvider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all main sections', () => {
    renderWithProviders()
    
    expect(screen.getByTestId('hero')).toBeInTheDocument()
    expect(screen.getAllByTestId('feature-card')).toHaveLength(4) // Assuming 4 features
    expect(screen.getAllByTestId('testimonial')).toHaveLength(3) // Assuming 3 testimonials
    expect(screen.getByTestId('faq')).toBeInTheDocument()
    expect(screen.getByTestId('cta')).toBeInTheDocument()
  })

  it('renders security statistics section', () => {
    renderWithProviders()
    
    expect(screen.getByText(/Sites Monitored/i)).toBeInTheDocument()
    expect(screen.getByText(/Security Issues Detected/i)).toBeInTheDocument()
    expect(screen.getByText(/Updates Tracked/i)).toBeInTheDocument()
  })

  it('renders how it works section', () => {
    renderWithProviders()
    
    expect(screen.getByText(/How It Works/i)).toBeInTheDocument()
    expect(screen.getByText(/Connect Your Sites/i)).toBeInTheDocument()
    expect(screen.getByText(/Monitor Security/i)).toBeInTheDocument()
    expect(screen.getByText(/Get Alerts/i)).toBeInTheDocument()
  })

  it('renders pricing preview section', () => {
    renderWithProviders()
    
    expect(screen.getByText(/Simple, Transparent Pricing/i)).toBeInTheDocument()
    expect(screen.getByText(/Starter/i)).toBeInTheDocument()
    expect(screen.getByText(/Professional/i)).toBeInTheDocument()
    expect(screen.getByText(/Enterprise/i)).toBeInTheDocument()
  })

  it('handles hero CTA click', async () => {
    renderWithProviders()
    
    const getStartedButton = screen.getByText('Get Started')
    await userEvent.click(getStartedButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup')
  })

  it('handles view pricing button click', async () => {
    renderWithProviders()
    
    const viewPricingButton = screen.getByText(/View Full Pricing/i)
    await userEvent.click(viewPricingButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/pricing')
  })

  it('handles learn more features click', async () => {
    renderWithProviders()
    
    const learnMoreButton = screen.getByText(/Learn More About Features/i)
    await userEvent.click(learnMoreButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/features')
  })

  it('sets correct meta tags for SEO', () => {
    renderWithProviders()
    
    waitFor(() => {
      const title = document.querySelector('title')
      expect(title?.textContent).toBe('Sentinel - Monitor Your Drupal Sites Security')
      
      const description = document.querySelector('meta[name="description"]')
      expect(description?.getAttribute('content')).toContain('Real-time security monitoring')
      
      const ogTitle = document.querySelector('meta[property="og:title"]')
      expect(ogTitle?.getAttribute('content')).toBe('Sentinel - Drupal Security Monitoring')
    })
  })

  it('renders animated counters for statistics', () => {
    renderWithProviders()
    
    const counters = screen.getAllByTestId('animated-counter')
    expect(counters).toHaveLength(3)
  })

  it('has smooth scroll behavior for internal links', async () => {
    renderWithProviders()
    
    const howItWorksLink = screen.getByText(/See How It Works/i)
    const originalScrollIntoView = Element.prototype.scrollIntoView
    Element.prototype.scrollIntoView = vi.fn()
    
    await userEvent.click(howItWorksLink)
    
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' })
    
    Element.prototype.scrollIntoView = originalScrollIntoView
  })

  it('renders trust indicators', () => {
    renderWithProviders()
    
    expect(screen.getByText(/SSL Encrypted/i)).toBeInTheDocument()
    expect(screen.getByText(/GDPR Compliant/i)).toBeInTheDocument()
    expect(screen.getByText(/99.9% Uptime/i)).toBeInTheDocument()
  })

  it('displays feature icons correctly', () => {
    renderWithProviders()
    
    const featureCards = screen.getAllByTestId('feature-card')
    expect(featureCards.length).toBeGreaterThan(0)
  })

  it('renders responsive layout classes', () => {
    const { container } = renderWithProviders()
    
    const sections = container.querySelectorAll('section')
    sections.forEach(section => {
      expect(section).toHaveClass('py-12', 'md:py-16', 'lg:py-20')
    })
  })

  it('handles newsletter form submission', async () => {
    renderWithProviders()
    
    const emailInput = screen.getByPlaceholderText(/Enter your email/i)
    const submitButton = screen.getByText(/Subscribe to Newsletter/i)
    
    await userEvent.type(emailInput, 'test@example.com')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Thank you for subscribing/i)).toBeInTheDocument()
    })
  })

  it('validates newsletter email format', async () => {
    renderWithProviders()
    
    const emailInput = screen.getByPlaceholderText(/Enter your email/i)
    const submitButton = screen.getByText(/Subscribe to Newsletter/i)
    
    await userEvent.type(emailInput, 'invalid-email')
    await userEvent.click(submitButton)
    
    expect(screen.getByText(/Please enter a valid email/i)).toBeInTheDocument()
  })

  it('lazy loads below-fold images', () => {
    renderWithProviders()
    
    const images = screen.getAllByRole('img')
    const belowFoldImages = images.slice(3) // Assuming first 3 are above fold
    
    belowFoldImages.forEach(img => {
      expect(img).toHaveAttribute('loading', 'lazy')
    })
  })

  it('renders structured data for SEO', () => {
    renderWithProviders()
    
    const structuredData = document.querySelector('script[type="application/ld+json"]')
    expect(structuredData).toBeInTheDocument()
    
    if (structuredData) {
      const data = JSON.parse(structuredData.textContent || '{}')
      expect(data['@type']).toBe('SoftwareApplication')
      expect(data.name).toBe('Sentinel')
    }
  })

  it('handles keyboard navigation correctly', async () => {
    renderWithProviders()
    
    const firstInteractiveElement = screen.getAllByRole('button')[0]
    firstInteractiveElement.focus()
    
    expect(document.activeElement).toBe(firstInteractiveElement)
  })

  it('displays loading state while fetching statistics', () => {
    renderWithProviders()
    
    // Initially shows loading state
    expect(screen.getAllByTestId('skeleton-loader')).toHaveLength(3)
    
    // After loading, shows actual numbers
    waitFor(() => {
      expect(screen.queryByTestId('skeleton-loader')).not.toBeInTheDocument()
      expect(screen.getByText(/\d+/)).toBeInTheDocument()
    })
  })

  it('handles error state for statistics gracefully', async () => {
    // Mock API error
    vi.spyOn(console, 'error').mockImplementation(() => {})
    
    renderWithProviders()
    
    await waitFor(() => {
      expect(screen.queryByText(/Failed to load/i)).not.toBeInTheDocument()
      // Should show default values on error
      expect(screen.getByText('1000+')).toBeInTheDocument()
    })
  })

  it('applies correct animations on scroll', async () => {
    const { container } = renderWithProviders()
    
    const animatedElements = container.querySelectorAll('[data-animate]')
    expect(animatedElements.length).toBeGreaterThan(0)
    
    // Simulate scroll
    fireEvent.scroll(window, { target: { scrollY: 500 } })
    
    await waitFor(() => {
      animatedElements.forEach(element => {
        expect(element).toHaveClass('animate-in')
      })
    })
  })
})