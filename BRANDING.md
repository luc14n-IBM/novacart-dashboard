# NovaCart Dashboard — Branding Guidelines

> This file is the single source of truth for all visual design decisions in the NovaCart Dashboard frontend.  
> When adding new components or pages, reference these tokens and rules to stay consistent.

---

## 0. Company Overview

- NovaCart is an online retailer that sells thousands of products to customers in 30+ countries.
- The company has account managers across multiple countries who need access to sales data to perform their jobs.
- NovaCart has a Data Engineering team and an analytics team that provide data and reports to account managers.

---

## 1. Color Palette

### Primary Colors

| Name        | Hex       | RGB              | CSS Variable        | Role                                      |
|-------------|-----------|------------------|---------------------|-------------------------------------------|
| Vivid Blue  | `#1C4EF5` | rgb(28, 78, 245) | `--blue`            | CTAs, links, key data highlights          |
| Navy        | `#051B3F` | rgb(5, 27, 63)   | `--text-primary`    | Headers, body text, dark backgrounds      |
| Teal        | `#00BFA5` | rgb(0, 191, 165) | `--accent`          | Success states, positive metrics          |
| Salmon      | `#FF6B6B` | rgb(255, 107, 107)| `--danger`         | Alerts, warnings, diagnostic indicators   |
| Deep Navy   | `#000D1F` | rgb(0, 13, 31)   | *(dark bg base)*    | Darkest background layer in dark mode     |

### Secondary Colors

| Name        | Hex       | RGB                | CSS Variable        | Role                                      |
|-------------|-----------|--------------------|---------------------|-------------------------------------------|
| Light Blue  | `#BBDEFB` | rgb(187, 222, 251) | `--border`, `--bg-section` | Card fills, borders, section backgrounds |
| Aqua Tint   | `#E0F7FA` | rgb(224, 247, 250) | *(available)*       | Subtle teal tints                         |
| Mint        | `#A8E6CF` | rgb(168, 230, 207) | `--mint`            | Positive outcomes, wellness indicators    |
| Blush       | `#FFCDD2` | rgb(255, 205, 210) | *(available)*       | Soft alert backgrounds                    |
| Cyan Tint   | `#C8F5F5` | rgb(200, 245, 245) | *(dark text-muted)* | Muted text in dark mode                   |
| Silver      | `#DCDCDC` | rgb(220, 220, 220) | *(available)*       | Neutral dividers                          |
| White       | `#FFFFFF` | rgb(255, 255, 255) | `--bg-card`         | Card surfaces, button text                |

---

## 2. CSS Variables

Defined in [`frontend/src/App.css`](frontend/src/App.css). Use these in all components — never hard-code hex values.

### Light Mode (`:root`)

```css
--bg-primary:    #F0F4FF;   /* page background — off-white blue tint */
--bg-card:       #FFFFFF;   /* card surfaces */
--bg-section:    #BBDEFB;   /* section / stat box fills */
--text-primary:  #051B3F;   /* body text, headings */
--text-secondary:#1C4EF5;   /* labels, filter bar text */
--text-muted:    #6B7C99;   /* placeholder, helper text */
--border:        #BBDEFB;   /* all borders */
--accent:        #00BFA5;   /* teal — success, confirm */
--blue:          #1C4EF5;   /* vivid blue — primary CTA */
--danger:        #FF6B6B;   /* salmon — alerts */
--mint:          #A8E6CF;   /* mint — positive outcomes */
--shadow:        0 2px 12px rgba(5,27,63,0.10);
--radius:        10px;
```

### Dark Mode (`[data-theme="dark"]`)

```css
--bg-primary:    #051B3F;   /* navy page background */
--bg-card:       #0A2550;   /* card surfaces */
--bg-section:    #0D2B5E;   /* section fills */
--text-primary:  #FFFFFF;   /* body text */
--text-secondary:#BBDEFB;   /* labels */
--text-muted:    #7A9CC4;   /* muted text */
--border:        #1C4EF5;   /* vivid blue borders */
/* accent, blue, danger, mint — unchanged from light */
```

---

## 3. Typography

### Font Family

**IBM Plex Sans** — loaded from Google Fonts in [`frontend/index.html`](frontend/index.html).

```
CSS variable: --font
Stack: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
Weights loaded: 300 (Light), 400 (Regular), 600 (SemiBold), 700 (Bold) + 400 Italic
```

### Type Scale

| Token        | Size  | CSS Variable    | Usage                              |
|--------------|-------|-----------------|------------------------------------|
| `--text-xs`  | 12px  | `var(--text-xs)` | Uppercase labels, stat box labels |
| `--text-sm`  | 13px  | `var(--text-sm)` | Buttons, filter labels, nav links |
| `--text-base`| 15px  | `var(--text-base)`| Body text                        |
| `--text-lg`  | 18px  | `var(--text-lg)` | h4, sub-headings                  |
| `--text-xl`  | 24px  | `var(--text-xl)` | h3, section titles, stat values   |
| `--text-2xl` | 32px  | `var(--text-2xl)`| h2                                |
| `--text-3xl` | 48px  | `var(--text-3xl)`| h1, impact headers                |

### Rules

| Rule             | Value                        |
|------------------|------------------------------|
| Heading weight   | **Bold (700)**               |
| Body weight      | Regular (400)                |
| Label weight     | SemiBold (600)               |
| Line height body | `1.5` (`--leading`)          |
| Line height heads| `1.2`                        |
| Alignment        | Left-aligned (all content)   |
| Max weights used | 3 — 400, 600, 700            |

### Heading Scale

```css
h1 — 48px Bold  — impact page headers ("Start Your Engines!")
h2 — 32px Bold  — major section headers
h3 — 24px Bold  — card/section headings  ← .section-title maps here
h4 — 18px Bold  — sub-section headings
```

---

## 4. Component Tokens

### Navbar
- Background: `#051B3F` (Navy — always, light and dark)
- Brand name: `#FFFFFF` Bold 18px
- "Dashboard" badge: `#00BFA5` (Teal) 12px
- Inactive nav links: `#BBDEFB` (Light Blue) SemiBold 13px
- Active nav link: `#FFFFFF` text, `#1C4EF5` border, `rgba(28,78,245,0.2)` background

### Cards (`.card`)
- Background: `--bg-card`
- Border: `1px solid --border`
- Border radius: `--radius` (10px)
- Shadow: `--shadow`

### Stat Boxes (`.stat-box`)
- Background: `--bg-section` (Light Blue fill)
- Left accent border: `4px solid --blue` (Vivid Blue)
- Label: 12px SemiBold uppercase, `--text-primary`
- Value: 24px Bold, `--blue`

### Buttons

| Class           | Background    | Text      | Use for                  |
|-----------------|---------------|-----------|--------------------------|
| `.btn-apply`    | `--blue`      | `#FFFFFF` | Primary CTA, Apply/Submit|
| `.btn-secondary`| transparent   | `--blue`  | Secondary actions        |
| `.btn-confirm`  | `--accent`    | `#051B3F` | Confirm, success actions |
| `.btn-alert`    | `--danger`    | `#FFFFFF` | Destructive, alert       |

All buttons: IBM Plex Sans SemiBold (600), 13px, border-radius 6px.

### Filter Bar (`.filter-bar`)
- Background: `--bg-card`
- Labels: SemiBold 13px, `--text-secondary`
- Inputs: `--bg-primary` background, `--border` border, 13px Regular

---

## 5. Layout

- **Max page width:** 1280px (`.page`)
- **Page padding:** 24px
- **Card gap:** 20px
- **Responsive breakpoint:** 900px — 2-col grid collapses to 1-col
- **Border radius:** 10px (`--radius`) on cards; 6px on inputs/buttons

---

## 6. Dark Mode

Dark mode is toggled by adding `data-theme="dark"` to the `<html>` element, managed via [`frontend/src/utils/ThemeContext.jsx`](frontend/src/utils/ThemeContext.jsx).

All color variables automatically swap — no component-level overrides needed as long as you use CSS variables.

---

## 7. Do's and Don'ts

**Do:**
- Always use CSS variables from `:root` — never hard-code hex values in components
- Use `--blue` for primary actions, `--accent` (teal) for success/confirm
- Use `--danger` (salmon) for errors, alerts, and destructive actions
- Use `var(--font)` or inherit font-family — never specify a different font

**Don't:**
- Don't use `font-weight: 500` — only 400, 600, 700 are loaded
- Don't center-align body or paragraph text
- Don't add new colors outside the palette without updating this file
- Don't hard-code `#051B3F` or any hex in JSX inline styles — use the CSS variable

---

## 8. Iconography

All icons are defined in [`frontend/src/components/Icons.jsx`](frontend/src/components/Icons.jsx).  
They use `currentColor`, a 16×16 viewBox, and outline style (1.2–1.5px stroke) so they inherit color from their parent automatically.

| Export | Description | Used In |
|---|---|---|
| `<CartGlobe />` | Shopping Cart + Globe | Navbar brand mark, LoginView |
| `<ProductGrid />` | Product Grid | ProductsView — Product Details section title |
| `<BarChartIcon />` | Bar Chart | OrdersView — Monthly Revenue title + Total Orders stat label |
| `<DocumentChart />` | Document + Chart | OrdersView — Total Revenue stat label |
| `<SearchGraph />` | Magnifying Glass + Graph | ProductsView — Top 10 Products section title |
| `<DatabaseGear />` | Database + Gear | ServiceStatus component in Navbar |
| `<FlowNodes />` | Connected Nodes / Flow Arrows | OrdersView filter bar (data pipeline indicator) |
| `<UserBriefcase />` | User + Briefcase | CustomersView — Top Customers section title |
| `<GlobePin />` | Globe + Location Pins | OrdersView — Revenue by City title + Unique Customers stat label |
| `<Gear />` | Gear | All filter bar Apply buttons across every view |

### Usage
```jsx
import { BarChartIcon, Gear } from '../components/Icons';

<div className="section-title">
  <BarChartIcon size={18} /> Monthly Revenue
</div>
```

- Default `size` is `16`. Pass `size={18}` for section titles, `size={13}` for buttons, `size={12}` for stat labels.
- Never hard-code a fill color — let `currentColor` inherit from the parent element.
