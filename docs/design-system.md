# Design System for Monitoring Platform

## Overview

This design system establishes the visual language, component patterns, and interaction guidelines for the Monitoring Platform frontend. It ensures consistency, accessibility, and a professional user experience across all interfaces.

## Design Principles

1. **Clarity First** - Information should be immediately understandable
2. **Data-Driven** - Visualizations should tell a story
3. **Responsive** - Works seamlessly across all devices
4. **Accessible** - WCAG 2.1 AA compliant
5. **Performance** - Fast loading and smooth interactions

## Color Palette

### Primary Colors
```scss
// Brand colors
$primary-50: #eff6ff;    // Lightest blue
$primary-100: #dbeafe;
$primary-200: #bfdbfe;
$primary-300: #93c5fd;
$primary-400: #60a5fa;
$primary-500: #3b82f6;   // Main brand blue
$primary-600: #2563eb;
$primary-700: #1d4ed8;
$primary-800: #1e40af;
$primary-900: #1e3a8a;   // Darkest blue

// Accent colors
$accent: #8b5cf6;        // Purple accent
$accent-hover: #7c3aed;
```

### Status Colors
```scss
// Semantic colors for system states
$success: #10b981;       // Green - healthy, up-to-date
$warning: #f59e0b;       // Amber - needs attention
$danger: #ef4444;        // Red - critical, security issues
$info: #3b82f6;          // Blue - informational

// Extended status palette
$success-light: #d1fae5;
$warning-light: #fef3c7;
$danger-light: #fee2e2;
$info-light: #dbeafe;
```

### Severity Colors
```scss
// Security severity levels
$critical: #991b1b;      // Dark red
$high: #dc2626;          // Red
$medium: #f59e0b;        // Amber
$low: #fbbf24;           // Yellow
$info: #3b82f6;          // Blue
```

### Neutral Colors
```scss
// Grayscale for UI elements
$gray-50: #f9fafb;       // Background
$gray-100: #f3f4f6;      // Light background
$gray-200: #e5e7eb;      // Borders
$gray-300: #d1d5db;      // Disabled
$gray-400: #9ca3af;      // Placeholder
$gray-500: #6b7280;      // Secondary text
$gray-600: #4b5563;      // Primary text
$gray-700: #374151;      // Headings
$gray-800: #1f2937;      // Dark text
$gray-900: #111827;      // Darkest text
```

## Typography

### Font Stack
```scss
$font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
            'Helvetica Neue', Arial, sans-serif;
$font-mono: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', 
            'Roboto Mono', monospace;
```

### Type Scale
```scss
// Font sizes
$text-xs: 0.75rem;       // 12px - captions, labels
$text-sm: 0.875rem;      // 14px - secondary text
$text-base: 1rem;        // 16px - body text
$text-lg: 1.125rem;      // 18px - large body
$text-xl: 1.25rem;       // 20px - section headers
$text-2xl: 1.5rem;       // 24px - page headers
$text-3xl: 1.875rem;     // 30px - major headers
$text-4xl: 2.25rem;      // 36px - hero text

// Line heights
$leading-tight: 1.25;
$leading-normal: 1.5;
$leading-relaxed: 1.75;

// Font weights
$font-normal: 400;
$font-medium: 500;
$font-semibold: 600;
$font-bold: 700;
```

### Text Styles
```scss
// Headings
.heading-1 {
  font-size: $text-3xl;
  font-weight: $font-bold;
  line-height: $leading-tight;
  color: $gray-900;
}

.heading-2 {
  font-size: $text-2xl;
  font-weight: $font-semibold;
  line-height: $leading-tight;
  color: $gray-800;
}

// Body text
.body-text {
  font-size: $text-base;
  font-weight: $font-normal;
  line-height: $leading-normal;
  color: $gray-600;
}

// Captions
.caption {
  font-size: $text-sm;
  font-weight: $font-normal;
  line-height: $leading-normal;
  color: $gray-500;
}
```

## Spacing System

### Base Unit
Our spacing system is based on a 4px grid:

```scss
$space-1: 0.25rem;   // 4px
$space-2: 0.5rem;    // 8px
$space-3: 0.75rem;   // 12px
$space-4: 1rem;      // 16px
$space-5: 1.25rem;   // 20px
$space-6: 1.5rem;    // 24px
$space-8: 2rem;      // 32px
$space-10: 2.5rem;   // 40px
$space-12: 3rem;     // 48px
$space-16: 4rem;     // 64px
$space-20: 5rem;     // 80px
$space-24: 6rem;     // 96px
```

## Layout Grid

### Container Widths
```scss
$container-sm: 640px;
$container-md: 768px;
$container-lg: 1024px;
$container-xl: 1280px;
$container-2xl: 1536px;
```

### Dashboard Grid
- 12-column grid system
- 20px gutters
- Responsive breakpoints:
  - Mobile: 1 column
  - Tablet: 6 columns
  - Desktop: 12 columns

## Components

### Buttons

#### Primary Button
```scss
.btn-primary {
  background: $primary-500;
  color: white;
  padding: $space-2 $space-4;
  border-radius: $radius-md;
  font-weight: $font-medium;
  
  &:hover {
    background: $primary-600;
  }
  
  &:disabled {
    background: $gray-300;
    cursor: not-allowed;
  }
}
```

#### Button Sizes
- Small: 32px height
- Medium: 40px height (default)
- Large: 48px height

### Cards

```scss
.card {
  background: white;
  border: 1px solid $gray-200;
  border-radius: $radius-lg;
  padding: $space-6;
  box-shadow: $shadow-sm;
  
  &:hover {
    box-shadow: $shadow-md;
  }
}
```

### Form Elements

#### Input Fields
```scss
.input {
  width: 100%;
  padding: $space-2 $space-3;
  border: 1px solid $gray-300;
  border-radius: $radius-md;
  font-size: $text-base;
  
  &:focus {
    outline: none;
    border-color: $primary-500;
    box-shadow: 0 0 0 3px $primary-100;
  }
  
  &.error {
    border-color: $danger;
  }
}
```

### Data Visualization

#### Chart Colors
```scss
// Sequential palette for data series
$chart-colors: (
  $primary-500,
  $accent,
  $success,
  $warning,
  $info,
  $primary-300,
  $accent-hover,
  $success-light
);

// Severity-based colors
$severity-colors: (
  critical: $critical,
  high: $high,
  medium: $medium,
  low: $low,
  info: $info
);
```

## Dashboard Widgets

### Widget Container
```scss
.widget {
  background: white;
  border: 1px solid $gray-200;
  border-radius: $radius-lg;
  padding: $space-4;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $space-4;
    
    h3 {
      font-size: $text-lg;
      font-weight: $font-semibold;
      color: $gray-800;
    }
  }
  
  .widget-body {
    flex: 1;
    overflow: auto;
  }
}
```

### Metric Cards
```scss
.metric-card {
  display: flex;
  flex-direction: column;
  gap: $space-2;
  
  .metric-value {
    font-size: $text-3xl;
    font-weight: $font-bold;
    color: $gray-900;
  }
  
  .metric-label {
    font-size: $text-sm;
    color: $gray-500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .metric-change {
    display: flex;
    align-items: center;
    gap: $space-1;
    font-size: $text-sm;
    
    &.positive {
      color: $success;
    }
    
    &.negative {
      color: $danger;
    }
  }
}
```

## Icons

### Icon Library
Using Lucide React icons for consistency:
- Size variants: 16px, 20px, 24px
- Stroke width: 2px
- Color: Inherit from parent

### Common Icons
```
Security: Shield, Lock, AlertTriangle
Status: CheckCircle, XCircle, AlertCircle, Info
Actions: Plus, Edit, Trash, Download, Share
Navigation: ChevronRight, ChevronDown, Menu, X
Data: BarChart, LineChart, PieChart, TrendingUp
```

## Animation & Transitions

### Timing Functions
```scss
$ease-in: cubic-bezier(0.4, 0, 1, 1);
$ease-out: cubic-bezier(0, 0, 0.2, 1);
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Durations
```scss
$duration-fast: 150ms;    // Hover states
$duration-normal: 250ms;  // Most transitions
$duration-slow: 350ms;    // Complex animations
```

### Common Transitions
```scss
.transition-all {
  transition: all $duration-normal $ease-in-out;
}

.transition-colors {
  transition: background-color $duration-fast $ease-in-out,
              border-color $duration-fast $ease-in-out,
              color $duration-fast $ease-in-out;
}
```

## Shadows & Elevation

```scss
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
            0 4px 6px -2px rgba(0, 0, 0, 0.05);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

## Border Radius

```scss
$radius-sm: 0.125rem;   // 2px
$radius-md: 0.375rem;   // 6px
$radius-lg: 0.5rem;     // 8px
$radius-xl: 0.75rem;    // 12px
$radius-full: 9999px;   // Circular
```

## Responsive Design

### Breakpoints
```scss
$breakpoint-sm: 640px;   // Mobile landscape
$breakpoint-md: 768px;   // Tablet
$breakpoint-lg: 1024px;  // Desktop
$breakpoint-xl: 1280px;  // Large desktop
$breakpoint-2xl: 1536px; // Extra large
```

### Mobile-First Approach
```scss
// Base styles (mobile)
.component {
  padding: $space-4;
}

// Tablet and up
@media (min-width: $breakpoint-md) {
  .component {
    padding: $space-6;
  }
}

// Desktop and up
@media (min-width: $breakpoint-lg) {
  .component {
    padding: $space-8;
  }
}
```

## Accessibility Guidelines

### Color Contrast
- Normal text: 4.5:1 ratio
- Large text: 3:1 ratio
- Interactive elements: 3:1 ratio

### Focus States
```scss
.focusable {
  &:focus {
    outline: 2px solid $primary-500;
    outline-offset: 2px;
  }
  
  &:focus:not(:focus-visible) {
    outline: none; // Remove for mouse users
  }
}
```

### ARIA Labels
- All interactive elements must have accessible names
- Use aria-label for icon-only buttons
- Provide screen reader announcements for dynamic content

## Dark Mode

### Dark Theme Colors
```scss
// Dark mode palette
$dark-bg: #0f172a;
$dark-surface: #1e293b;
$dark-border: #334155;
$dark-text: #f1f5f9;
$dark-text-secondary: #cbd5e1;
```

### Implementation
```scss
[data-theme="dark"] {
  --bg-primary: #{$dark-bg};
  --bg-surface: #{$dark-surface};
  --border-color: #{$dark-border};
  --text-primary: #{$dark-text};
  --text-secondary: #{$dark-text-secondary};
}
```

## Component Examples

### Security Alert Card
```tsx
<div className="alert alert-danger">
  <AlertTriangle className="alert-icon" />
  <div className="alert-content">
    <h4 className="alert-title">Critical Security Update</h4>
    <p className="alert-description">
      3 modules require immediate security patches
    </p>
  </div>
  <button className="alert-action">View Details</button>
</div>
```

### Module Status Badge
```tsx
<span className={`badge badge-${status}`}>
  {status === 'critical' && <AlertCircle size={14} />}
  {status === 'up-to-date' && <CheckCircle size={14} />}
  {label}
</span>
```

### Dashboard Widget Grid
```tsx
<div className="dashboard-grid">
  <div className="widget col-span-4">
    <SecuritySummaryWidget />
  </div>
  <div className="widget col-span-4">
    <ModuleUpdatesWidget />
  </div>
  <div className="widget col-span-4">
    <ComplianceGaugeWidget />
  </div>
</div>
```

## Best Practices

1. **Consistency** - Use established patterns and components
2. **Hierarchy** - Clear visual hierarchy guides user attention
3. **Feedback** - Immediate feedback for all interactions
4. **Progressive Disclosure** - Show details on demand
5. **Error Prevention** - Validate inputs and confirm destructive actions
6. **Performance** - Optimize for fast load times and smooth interactions

## Implementation Notes

1. Use CSS custom properties for theming
2. Implement responsive typography with clamp()
3. Use CSS Grid for dashboard layouts
4. Leverage Tailwind utilities where appropriate
5. Ensure all components are keyboard navigable
6. Test with screen readers and color blind simulators