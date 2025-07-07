import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PricingCard } from './PricingCard'

describe('PricingCard', () => {
  const defaultProps = {
    planName: 'Professional',
    price: 99,
    currency: '$',
    period: 'month' as const,
    features: [
      'Up to 50 sites',
      'Real-time monitoring',
      'API access',
      'Email & Chat support',
    ],
    onSelect: vi.fn(),
  }

  it('renders plan name and price', () => {
    render(<PricingCard {...defaultProps} />)
    
    expect(screen.getByText(defaultProps.planName)).toBeInTheDocument()
    expect(screen.getByText(`${defaultProps.currency}${defaultProps.price}`)).toBeInTheDocument()
    expect(screen.getByText(`/${defaultProps.period}`)).toBeInTheDocument()
  })

  it('renders all features with checkmarks', () => {
    render(<PricingCard {...defaultProps} />)
    
    defaultProps.features.forEach(feature => {
      expect(screen.getByText(feature)).toBeInTheDocument()
    })
    
    const checkmarks = screen.getAllByTestId('checkmark-icon')
    expect(checkmarks).toHaveLength(defaultProps.features.length)
  })

  it('handles select button click', async () => {
    render(<PricingCard {...defaultProps} />)
    
    const selectButton = screen.getByText(`Select ${defaultProps.planName}`)
    await userEvent.click(selectButton)
    
    expect(defaultProps.onSelect).toHaveBeenCalledTimes(1)
  })

  it('shows recommended badge', () => {
    render(<PricingCard {...defaultProps} isRecommended />)
    
    expect(screen.getByText('Recommended')).toBeInTheDocument()
    const card = screen.getByTestId('pricing-card')
    expect(card).toHaveClass('border-primary-500', 'shadow-xl')
  })

  it('renders custom CTA text', () => {
    const ctaText = 'Start Free Trial'
    render(<PricingCard {...defaultProps} ctaText={ctaText} />)
    
    expect(screen.getByText(ctaText)).toBeInTheDocument()
    expect(screen.queryByText(`Select ${defaultProps.planName}`)).not.toBeInTheDocument()
  })

  it('shows original price with discount', () => {
    const originalPrice = 120
    render(<PricingCard {...defaultProps} originalPrice={originalPrice} />)
    
    const strikethroughPrice = screen.getByText(`${defaultProps.currency}${originalPrice}`)
    expect(strikethroughPrice).toBeInTheDocument()
    expect(strikethroughPrice).toHaveClass('line-through', 'text-neutral-500')
  })

  it('displays savings badge', () => {
    const originalPrice = 120
    render(<PricingCard {...defaultProps} originalPrice={originalPrice} />)
    
    const savings = originalPrice - defaultProps.price
    const savingsPercentage = Math.round((savings / originalPrice) * 100)
    
    expect(screen.getByText(`Save ${savingsPercentage}%`)).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    const description = 'Perfect for growing agencies'
    render(<PricingCard {...defaultProps} description={description} />)
    
    expect(screen.getByText(description)).toBeInTheDocument()
  })

  it('shows custom price text', () => {
    const customPriceText = 'Contact us'
    render(<PricingCard {...defaultProps} price={customPriceText} />)
    
    expect(screen.getByText(customPriceText)).toBeInTheDocument()
  })

  it('renders with annual billing display', () => {
    render(<PricingCard {...defaultProps} period="year" billingNote="billed annually" />)
    
    expect(screen.getByText('/year')).toBeInTheDocument()
    expect(screen.getByText('billed annually')).toBeInTheDocument()
  })

  it('shows per month price for annual plans', () => {
    const annualPrice = 950
    const monthlyEquivalent = Math.round(annualPrice / 12)
    
    render(
      <PricingCard 
        {...defaultProps} 
        price={annualPrice}
        period="year"
        showMonthlyEquivalent
      />
    )
    
    expect(screen.getByText(`${defaultProps.currency}${monthlyEquivalent}/month`)).toBeInTheDocument()
  })

  it('disables selection when disabled prop is true', async () => {
    render(<PricingCard {...defaultProps} disabled />)
    
    const selectButton = screen.getByText(`Select ${defaultProps.planName}`)
    expect(selectButton).toBeDisabled()
    
    await userEvent.click(selectButton)
    expect(defaultProps.onSelect).not.toHaveBeenCalled()
  })

  it('shows coming soon state', () => {
    render(<PricingCard {...defaultProps} comingSoon />)
    
    expect(screen.getByText('Coming Soon')).toBeInTheDocument()
    const selectButton = screen.getByText(`Select ${defaultProps.planName}`)
    expect(selectButton).toBeDisabled()
  })

  it('renders feature groups', () => {
    const featureGroups = [
      {
        title: 'Monitoring',
        features: ['Real-time tracking', 'Security scanning']
      },
      {
        title: 'Support',
        features: ['Email support', 'Chat support']
      }
    ]
    
    render(<PricingCard {...defaultProps} featureGroups={featureGroups} />)
    
    featureGroups.forEach(group => {
      expect(screen.getByText(group.title)).toBeInTheDocument()
      group.features.forEach(feature => {
        expect(screen.getByText(feature)).toBeInTheDocument()
      })
    })
  })

  it('shows unavailable features with cross mark', () => {
    const allFeatures = [
      { text: 'Basic monitoring', available: true },
      { text: 'Advanced analytics', available: false },
      { text: 'API access', available: true },
      { text: 'White-label reports', available: false },
    ]
    
    render(<PricingCard {...defaultProps} detailedFeatures={allFeatures} />)
    
    const checkmarks = screen.getAllByTestId('checkmark-icon')
    const crossmarks = screen.getAllByTestId('crossmark-icon')
    
    expect(checkmarks).toHaveLength(2)
    expect(crossmarks).toHaveLength(2)
  })

  it('renders highlight text', () => {
    const highlight = 'Most Popular'
    render(<PricingCard {...defaultProps} highlight={highlight} />)
    
    expect(screen.getByText(highlight)).toBeInTheDocument()
  })

  it('shows limits for features', () => {
    const featuresWithLimits = [
      { text: 'Sites', limit: '50' },
      { text: 'API calls', limit: '100K/month' },
      { text: 'Users', limit: 'Unlimited' },
    ]
    
    render(<PricingCard {...defaultProps} featuresWithLimits={featuresWithLimits} />)
    
    featuresWithLimits.forEach(feature => {
      expect(screen.getByText(feature.text)).toBeInTheDocument()
      expect(screen.getByText(feature.limit)).toBeInTheDocument()
    })
  })

  it('applies custom color scheme', () => {
    render(<PricingCard {...defaultProps} color="success" />)
    
    const selectButton = screen.getByText(`Select ${defaultProps.planName}`)
    expect(selectButton).toHaveClass('bg-success-600', 'hover:bg-success-700')
  })

  it('renders guarantee text', () => {
    const guarantee = '30-day money-back guarantee'
    render(<PricingCard {...defaultProps} guarantee={guarantee} />)
    
    expect(screen.getByText(guarantee)).toBeInTheDocument()
    expect(screen.getByTestId('shield-icon')).toBeInTheDocument()
  })

  it('shows setup fee when applicable', () => {
    const setupFee = 199
    render(<PricingCard {...defaultProps} setupFee={setupFee} />)
    
    expect(screen.getByText(`+ ${defaultProps.currency}${setupFee} setup fee`)).toBeInTheDocument()
  })

  it('displays free trial information', () => {
    const trial = {
      duration: 14,
      text: '14-day free trial'
    }
    
    render(<PricingCard {...defaultProps} trial={trial} />)
    
    expect(screen.getByText(trial.text)).toBeInTheDocument()
  })

  it('handles hover state', () => {
    render(<PricingCard {...defaultProps} />)
    
    const card = screen.getByTestId('pricing-card')
    fireEvent.mouseEnter(card)
    
    expect(card).toHaveClass('shadow-lg')
  })

  it('renders custom badge', () => {
    const badge = {
      text: 'Limited Time',
      color: 'danger' as const
    }
    
    render(<PricingCard {...defaultProps} badge={badge} />)
    
    const badgeElement = screen.getByText(badge.text)
    expect(badgeElement).toBeInTheDocument()
    expect(badgeElement).toHaveClass('bg-danger-100', 'text-danger-800')
  })

  it('shows user count', () => {
    const users = {
      included: 5,
      additional: 10,
      additionalCost: 10
    }
    
    render(<PricingCard {...defaultProps} users={users} />)
    
    expect(screen.getByText(`${users.included} users included`)).toBeInTheDocument()
    expect(screen.getByText(`+${defaultProps.currency}${users.additionalCost} per additional user`)).toBeInTheDocument()
  })

  it('renders footer notes', () => {
    const footerNotes = [
      'No credit card required',
      'Cancel anytime'
    ]
    
    render(<PricingCard {...defaultProps} footerNotes={footerNotes} />)
    
    footerNotes.forEach(note => {
      expect(screen.getByText(note)).toBeInTheDocument()
    })
  })

  it('supports loading state', () => {
    render(<PricingCard {...defaultProps} loading />)
    
    expect(screen.getByTestId('pricing-skeleton')).toBeInTheDocument()
    expect(screen.queryByText(defaultProps.planName)).not.toBeInTheDocument()
  })

  it('handles keyboard navigation', async () => {
    render(<PricingCard {...defaultProps} />)
    
    const selectButton = screen.getByText(`Select ${defaultProps.planName}`)
    selectButton.focus()
    
    fireEvent.keyDown(selectButton, { key: 'Enter' })
    expect(defaultProps.onSelect).toHaveBeenCalledTimes(1)
  })

  it('shows comparison helper', () => {
    render(<PricingCard {...defaultProps} showComparison />)
    
    const compareButton = screen.getByText('Compare plans')
    expect(compareButton).toBeInTheDocument()
  })

  it('renders with compact layout', () => {
    render(<PricingCard {...defaultProps} layout="compact" />)
    
    const card = screen.getByTestId('pricing-card')
    expect(card).toHaveClass('p-4')
  })

  it('displays addon options', () => {
    const addons = [
      { name: 'Extra storage', price: 20 },
      { name: 'Priority support', price: 50 }
    ]
    
    render(<PricingCard {...defaultProps} addons={addons} />)
    
    expect(screen.getByText('Available add-ons:')).toBeInTheDocument()
    addons.forEach(addon => {
      expect(screen.getByText(addon.name)).toBeInTheDocument()
      expect(screen.getByText(`+${defaultProps.currency}${addon.price}`)).toBeInTheDocument()
    })
  })

  it('shows enterprise contact option', () => {
    render(<PricingCard {...defaultProps} isEnterprise ctaText="Contact Sales" />)
    
    const contactButton = screen.getByText('Contact Sales')
    expect(contactButton).toBeInTheDocument()
    expect(screen.getByText('Custom pricing for your needs')).toBeInTheDocument()
  })

  it('applies scale animation on recommended card', () => {
    render(<PricingCard {...defaultProps} isRecommended animated />)
    
    const card = screen.getByTestId('pricing-card')
    expect(card).toHaveClass('scale-105')
  })
})