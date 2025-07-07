import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { FeaturesPage } from './FeaturesPage'

// Mock navigation
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

// Mock components
vi.mock('../../../components/public/Hero/Hero', () => ({
  Hero: ({ title, subtitle }: { title: string; subtitle: string }) => (
    <div data-testid="hero">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  )
}))

vi.mock('../../../components/public/FeatureCard/FeatureCard', () => ({
  FeatureCard: ({ title, category }: { title: string; category?: string }) => (
    <div data-testid="feature-card" data-category={category}>
      {title}
    </div>
  )
}))

describe('FeaturesPage', () => {
  const renderWithProviders = () => {
    return render(
      <HelmetProvider>
        <MemoryRouter>
          <FeaturesPage />
        </MemoryRouter>
      </HelmetProvider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders hero section with correct content', () => {
    renderWithProviders()
    
    expect(screen.getByText('Powerful Features for Drupal Security')).toBeInTheDocument()
    expect(screen.getByText(/Comprehensive monitoring and reporting/i)).toBeInTheDocument()
  })

  it('renders navigation menu for feature sections', () => {
    renderWithProviders()
    
    expect(screen.getByText('Monitoring')).toBeInTheDocument()
    expect(screen.getByText('Security')).toBeInTheDocument()
    expect(screen.getByText('Reporting')).toBeInTheDocument()
    expect(screen.getByText('Integration')).toBeInTheDocument()
  })

  it('renders all monitoring features', () => {
    renderWithProviders()
    
    expect(screen.getByText('Real-time Module Tracking')).toBeInTheDocument()
    expect(screen.getByText('Security Update Detection')).toBeInTheDocument()
    expect(screen.getByText('Version Comparison')).toBeInTheDocument()
    expect(screen.getByText('Multi-site Dashboard')).toBeInTheDocument()
  })

  it('renders all security features', () => {
    renderWithProviders()
    
    expect(screen.getByText('Vulnerability Scanning')).toBeInTheDocument()
    expect(screen.getByText('Security Advisories')).toBeInTheDocument()
    expect(screen.getByText('Patch Management')).toBeInTheDocument()
    expect(screen.getByText('Compliance Tracking')).toBeInTheDocument()
  })

  it('renders all reporting features', () => {
    renderWithProviders()
    
    expect(screen.getByText('Executive Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Custom Reports')).toBeInTheDocument()
    expect(screen.getByText('Export Capabilities')).toBeInTheDocument()
    expect(screen.getByText('Scheduled Reports')).toBeInTheDocument()
  })

  it('renders all integration features', () => {
    renderWithProviders()
    
    expect(screen.getByText('REST API')).toBeInTheDocument()
    expect(screen.getByText('Webhook Support')).toBeInTheDocument()
    expect(screen.getByText('CI/CD Integration')).toBeInTheDocument()
    expect(screen.getByText('Slack Notifications')).toBeInTheDocument()
  })

  it('handles navigation menu clicks with smooth scroll', async () => {
    renderWithProviders()
    
    const monitoringTab = screen.getByText('Monitoring')
    const originalScrollIntoView = Element.prototype.scrollIntoView
    Element.prototype.scrollIntoView = vi.fn()
    
    await userEvent.click(monitoringTab)
    
    const monitoringSection = document.getElementById('monitoring-section')
    expect(monitoringSection).toBeInTheDocument()
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' })
    
    Element.prototype.scrollIntoView = originalScrollIntoView
  })

  it('highlights active section in navigation', async () => {
    renderWithProviders()
    
    // Simulate scrolling to security section
    const securitySection = document.getElementById('security-section')
    if (securitySection) {
      fireEvent.scroll(window, { target: { scrollY: securitySection.offsetTop } })
    }
    
    await waitFor(() => {
      const securityTab = screen.getByText('Security')
      expect(securityTab.parentElement).toHaveClass('border-primary-600')
    })
  })

  it('renders feature comparison table', () => {
    renderWithProviders()
    
    expect(screen.getByText('Feature Comparison')).toBeInTheDocument()
    expect(screen.getByRole('table')).toBeInTheDocument()
    
    // Check table headers
    expect(screen.getByText('Feature')).toBeInTheDocument()
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('displays correct checkmarks in comparison table', () => {
    renderWithProviders()
    
    const checkmarks = screen.getAllByTestId('checkmark-icon')
    expect(checkmarks.length).toBeGreaterThan(0)
    
    const crosses = screen.getAllByTestId('cross-icon')
    expect(crosses.length).toBeGreaterThan(0)
  })

  it('renders CTA section at the bottom', () => {
    renderWithProviders()
    
    expect(screen.getByText(/Ready to secure your Drupal sites?/i)).toBeInTheDocument()
    expect(screen.getByText('Start Free Trial')).toBeInTheDocument()
    expect(screen.getByText('Contact Sales')).toBeInTheDocument()
  })

  it('handles Start Free Trial button click', async () => {
    renderWithProviders()
    
    const startTrialButton = screen.getByText('Start Free Trial')
    await userEvent.click(startTrialButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup')
  })

  it('handles Contact Sales button click', async () => {
    renderWithProviders()
    
    const contactButton = screen.getByText('Contact Sales')
    await userEvent.click(contactButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/contact')
  })

  it('sets correct meta tags for SEO', () => {
    renderWithProviders()
    
    waitFor(() => {
      const title = document.querySelector('title')
      expect(title?.textContent).toBe('Features - Sentinel Drupal Monitoring')
      
      const description = document.querySelector('meta[name="description"]')
      expect(description?.getAttribute('content')).toContain('Comprehensive features for Drupal security monitoring')
    })
  })

  it('renders feature icons', () => {
    renderWithProviders()
    
    const featureCards = screen.getAllByTestId('feature-card')
    expect(featureCards.length).toBeGreaterThan(0)
  })

  it('applies correct responsive layout', () => {
    const { container } = renderWithProviders()
    
    const featureGrid = container.querySelector('.grid')
    expect(featureGrid).toHaveClass('md:grid-cols-2', 'lg:grid-cols-3')
  })

  it('shows feature details on card click', async () => {
    renderWithProviders()
    
    const featureCard = screen.getByText('Real-time Module Tracking')
    await userEvent.click(featureCard)
    
    await waitFor(() => {
      expect(screen.getByTestId('feature-modal')).toBeInTheDocument()
      expect(screen.getByText(/Track all modules across your Drupal sites/i)).toBeInTheDocument()
    })
  })

  it('filters features by search', async () => {
    renderWithProviders()
    
    const searchInput = screen.getByPlaceholderText('Search features...')
    await userEvent.type(searchInput, 'security')
    
    await waitFor(() => {
      const visibleFeatures = screen.getAllByTestId('feature-card')
      visibleFeatures.forEach(feature => {
        const text = feature.textContent?.toLowerCase()
        expect(text).toContain('security')
      })
    })
  })

  it('handles keyboard navigation for tabs', async () => {
    renderWithProviders()
    
    const firstTab = screen.getByText('Monitoring')
    firstTab.focus()
    
    // Press arrow right
    fireEvent.keyDown(firstTab, { key: 'ArrowRight' })
    
    await waitFor(() => {
      expect(document.activeElement?.textContent).toBe('Security')
    })
  })

  it('displays loading state for feature cards', () => {
    renderWithProviders()
    
    // Initially shows skeletons
    expect(screen.getAllByTestId('skeleton-loader')).toHaveLength(16) // 4 features x 4 categories
    
    // After loading
    waitFor(() => {
      expect(screen.queryByTestId('skeleton-loader')).not.toBeInTheDocument()
    })
  })

  it('shows feature availability badges', () => {
    renderWithProviders()
    
    expect(screen.getAllByText('Pro')).toHaveLength(4) // Some features marked as Pro only
    expect(screen.getAllByText('Enterprise')).toHaveLength(2) // Some features Enterprise only
  })

  it('renders screenshots for key features', () => {
    renderWithProviders()
    
    const screenshots = screen.getAllByAltText(/screenshot/i)
    expect(screenshots.length).toBeGreaterThan(0)
    
    screenshots.forEach(img => {
      expect(img).toHaveAttribute('loading', 'lazy')
    })
  })

  it('handles API documentation link', async () => {
    renderWithProviders()
    
    const apiDocLink = screen.getByText('View API Documentation')
    expect(apiDocLink).toHaveAttribute('href', '/api/docs')
    expect(apiDocLink).toHaveAttribute('target', '_blank')
    expect(apiDocLink).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('shows integration logos', () => {
    renderWithProviders()
    
    expect(screen.getByAltText('Slack Logo')).toBeInTheDocument()
    expect(screen.getByAltText('GitHub Logo')).toBeInTheDocument()
    expect(screen.getByAltText('GitLab Logo')).toBeInTheDocument()
  })

  it('handles mobile menu for feature navigation', async () => {
    // Mock mobile viewport
    window.innerWidth = 375
    
    renderWithProviders()
    
    const mobileMenuButton = screen.getByLabelText('Select feature category')
    await userEvent.click(mobileMenuButton)
    
    expect(screen.getByRole('listbox')).toBeInTheDocument()
  })

  it('applies correct animations on scroll', async () => {
    const { container } = renderWithProviders()
    
    const animatedElements = container.querySelectorAll('[data-animate-on-scroll]')
    
    // Simulate scroll
    fireEvent.scroll(window, { target: { scrollY: 500 } })
    
    await waitFor(() => {
      animatedElements.forEach(element => {
        expect(element).toHaveClass('opacity-100', 'translate-y-0')
      })
    })
  })
})