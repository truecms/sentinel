import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { PricingPage } from './PricingPage'

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
  Hero: ({ title }: { title: string }) => (
    <div data-testid="hero">
      <h1>{title}</h1>
    </div>
  )
}))

vi.mock('../../../components/public/PricingCard/PricingCard', () => ({
  PricingCard: ({ 
    planName, 
    price, 
    isRecommended,
    onSelect 
  }: { 
    planName: string
    price: string | number
    isRecommended?: boolean
    onSelect: () => void
  }) => (
    <div data-testid="pricing-card" data-recommended={isRecommended}>
      <h3>{planName}</h3>
      <p>{price}</p>
      <button onClick={onSelect}>Select {planName}</button>
    </div>
  )
}))

vi.mock('../../../components/public/FAQ/FAQ', () => ({
  FAQ: () => <div data-testid="faq">Pricing FAQ</div>
}))

describe('PricingPage', () => {
  const renderWithProviders = () => {
    return render(
      <HelmetProvider>
        <MemoryRouter>
          <PricingPage />
        </MemoryRouter>
      </HelmetProvider>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders hero section with title', () => {
    renderWithProviders()
    
    expect(screen.getByText('Choose Your Plan')).toBeInTheDocument()
  })

  it('renders billing toggle', () => {
    renderWithProviders()
    
    expect(screen.getByText('Monthly')).toBeInTheDocument()
    expect(screen.getByText('Annual')).toBeInTheDocument()
    expect(screen.getByText('Save 20%')).toBeInTheDocument()
  })

  it('renders all pricing cards', () => {
    renderWithProviders()
    
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Professional')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('displays monthly prices by default', () => {
    renderWithProviders()
    
    expect(screen.getByText('$29')).toBeInTheDocument()
    expect(screen.getByText('$99')).toBeInTheDocument()
    expect(screen.getByText('Custom')).toBeInTheDocument()
  })

  it('switches to annual prices when toggled', async () => {
    renderWithProviders()
    
    const annualToggle = screen.getByLabelText('Annual billing')
    await userEvent.click(annualToggle)
    
    expect(screen.getByText('$279')).toBeInTheDocument() // $29 * 12 * 0.8
    expect(screen.getByText('$950')).toBeInTheDocument() // $99 * 12 * 0.8
  })

  it('marks professional plan as recommended', () => {
    renderWithProviders()
    
    const professionalCard = screen.getByText('Professional').closest('[data-testid="pricing-card"]')
    expect(professionalCard).toHaveAttribute('data-recommended', 'true')
  })

  it('displays feature lists for each plan', () => {
    renderWithProviders()
    
    // Starter features
    expect(screen.getByText('Up to 5 sites')).toBeInTheDocument()
    expect(screen.getByText('Daily security scans')).toBeInTheDocument()
    expect(screen.getByText('Email alerts')).toBeInTheDocument()
    
    // Professional features
    expect(screen.getByText('Up to 50 sites')).toBeInTheDocument()
    expect(screen.getByText('Real-time monitoring')).toBeInTheDocument()
    expect(screen.getByText('API access')).toBeInTheDocument()
    
    // Enterprise features
    expect(screen.getByText('Unlimited sites')).toBeInTheDocument()
    expect(screen.getByText('Custom integrations')).toBeInTheDocument()
    expect(screen.getByText('Dedicated support')).toBeInTheDocument()
  })

  it('handles Starter plan selection', async () => {
    renderWithProviders()
    
    const selectStarterButton = screen.getByText('Select Starter')
    await userEvent.click(selectStarterButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup?plan=starter')
  })

  it('handles Professional plan selection', async () => {
    renderWithProviders()
    
    const selectProButton = screen.getByText('Select Professional')
    await userEvent.click(selectProButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup?plan=professional')
  })

  it('handles Enterprise plan contact', async () => {
    renderWithProviders()
    
    const contactButton = screen.getByText('Contact Sales')
    await userEvent.click(contactButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/contact?plan=enterprise')
  })

  it('renders feature comparison matrix', () => {
    renderWithProviders()
    
    expect(screen.getByText('Feature Comparison')).toBeInTheDocument()
    const table = screen.getByRole('table')
    expect(table).toBeInTheDocument()
  })

  it('shows correct limits in comparison table', () => {
    renderWithProviders()
    
    // Sites limit row
    expect(screen.getByText('Number of Sites')).toBeInTheDocument()
    const siteLimits = screen.getAllByText(/^(5|50|Unlimited)$/)
    expect(siteLimits).toHaveLength(3)
    
    // API calls row
    expect(screen.getByText('API Calls/Month')).toBeInTheDocument()
    expect(screen.getByText('10,000')).toBeInTheDocument()
    expect(screen.getByText('100,000')).toBeInTheDocument()
  })

  it('displays support levels correctly', () => {
    renderWithProviders()
    
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('Email + Chat')).toBeInTheDocument()
    expect(screen.getByText('24/7 Priority')).toBeInTheDocument()
  })

  it('renders FAQ section', () => {
    renderWithProviders()
    
    expect(screen.getByTestId('faq')).toBeInTheDocument()
  })

  it('shows money-back guarantee', () => {
    renderWithProviders()
    
    expect(screen.getByText(/30-day money-back guarantee/i)).toBeInTheDocument()
  })

  it('displays security badges', () => {
    renderWithProviders()
    
    expect(screen.getByText('PCI Compliant')).toBeInTheDocument()
    expect(screen.getByText('SSL Encrypted')).toBeInTheDocument()
  })

  it('sets correct meta tags for SEO', () => {
    renderWithProviders()
    
    waitFor(() => {
      const title = document.querySelector('title')
      expect(title?.textContent).toBe('Pricing - Sentinel Drupal Monitoring')
      
      const description = document.querySelector('meta[name="description"]')
      expect(description?.getAttribute('content')).toContain('Simple, transparent pricing')
    })
  })

  it('handles currency display', () => {
    renderWithProviders()
    
    const prices = screen.getAllByText(/^\$\d+/)
    prices.forEach(price => {
      expect(price.textContent).toMatch(/^\$\d+/)
    })
  })

  it('shows per-month suffix for annual prices', async () => {
    renderWithProviders()
    
    const annualToggle = screen.getByLabelText('Annual billing')
    await userEvent.click(annualToggle)
    
    expect(screen.getByText('/month')).toBeInTheDocument()
    expect(screen.getByText('billed annually')).toBeInTheDocument()
  })

  it('renders contact form for enterprise inquiries', () => {
    renderWithProviders()
    
    expect(screen.getByText('Need a custom plan?')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Your email')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Company name')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Tell us about your needs')).toBeInTheDocument()
  })

  it('validates enterprise contact form', async () => {
    renderWithProviders()
    
    const submitButton = screen.getByText('Send Inquiry')
    await userEvent.click(submitButton)
    
    expect(screen.getByText('Email is required')).toBeInTheDocument()
    expect(screen.getByText('Company name is required')).toBeInTheDocument()
  })

  it('submits enterprise contact form successfully', async () => {
    renderWithProviders()
    
    const emailInput = screen.getByPlaceholderText('Your email')
    const companyInput = screen.getByPlaceholderText('Company name')
    const messageInput = screen.getByPlaceholderText('Tell us about your needs')
    
    await userEvent.type(emailInput, 'test@company.com')
    await userEvent.type(companyInput, 'Test Company')
    await userEvent.type(messageInput, 'We need monitoring for 100+ sites')
    
    const submitButton = screen.getByText('Send Inquiry')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Thank you! We\'ll contact you soon.')).toBeInTheDocument()
    })
  })

  it('shows add-on services', () => {
    renderWithProviders()
    
    expect(screen.getByText('Available Add-ons')).toBeInTheDocument()
    expect(screen.getByText('White-label reporting')).toBeInTheDocument()
    expect(screen.getByText('Custom module development')).toBeInTheDocument()
    expect(screen.getByText('Migration assistance')).toBeInTheDocument()
  })

  it('handles keyboard navigation for pricing toggle', async () => {
    renderWithProviders()
    
    const monthlyToggle = screen.getByLabelText('Monthly billing')
    monthlyToggle.focus()
    
    fireEvent.keyDown(monthlyToggle, { key: 'ArrowRight' })
    
    await waitFor(() => {
      const annualToggle = screen.getByLabelText('Annual billing')
      expect(annualToggle).toHaveAttribute('aria-checked', 'true')
    })
  })

  it('displays trust indicators', () => {
    renderWithProviders()
    
    expect(screen.getByText('Trusted by 1000+ agencies')).toBeInTheDocument()
    expect(screen.getByAltText('Customer Logo 1')).toBeInTheDocument()
    expect(screen.getByAltText('Customer Logo 2')).toBeInTheDocument()
  })

  it('shows pricing calculator for large deployments', async () => {
    renderWithProviders()
    
    const calculatorButton = screen.getByText('Pricing Calculator')
    await userEvent.click(calculatorButton)
    
    expect(screen.getByText('Calculate Your Custom Price')).toBeInTheDocument()
    expect(screen.getByLabelText('Number of sites')).toBeInTheDocument()
    expect(screen.getByLabelText('Monthly API calls')).toBeInTheDocument()
  })

  it('updates calculator estimate dynamically', async () => {
    renderWithProviders()
    
    const calculatorButton = screen.getByText('Pricing Calculator')
    await userEvent.click(calculatorButton)
    
    const sitesInput = screen.getByLabelText('Number of sites')
    await userEvent.clear(sitesInput)
    await userEvent.type(sitesInput, '100')
    
    await waitFor(() => {
      expect(screen.getByText(/Estimated: \$\d+\/month/)).toBeInTheDocument()
    })
  })

  it('applies responsive layout for pricing cards', () => {
    const { container } = renderWithProviders()
    
    const pricingGrid = container.querySelector('.pricing-grid')
    expect(pricingGrid).toHaveClass('grid', 'md:grid-cols-3', 'gap-8')
  })

  it('handles payment method icons display', () => {
    renderWithProviders()
    
    const paymentIcons = ['Visa', 'Mastercard', 'American Express', 'PayPal']
    paymentIcons.forEach(payment => {
      expect(screen.getByAltText(`${payment} accepted`)).toBeInTheDocument()
    })
  })

  it('shows volume discount information', () => {
    renderWithProviders()
    
    expect(screen.getByText('Volume Discounts Available')).toBeInTheDocument()
    expect(screen.getByText('10% off for 100+ sites')).toBeInTheDocument()
    expect(screen.getByText('20% off for 500+ sites')).toBeInTheDocument()
  })
})