# ORBIS CI Color Palette

This directory contains the official ORBIS Corporate Identity color palette definitions based on the corporate style guide.

## Files

- **`color-palette.ts`** - TypeScript color definitions for use in components and services
- **`_color-palette.scss`** - SCSS/CSS variables for use in stylesheets

## Usage

### In TypeScript/JavaScript

```typescript
import { ORBIS_COLORS, getOrbisColor } from '@app/assets/color-palette';

// Direct access
const primaryBlue = ORBIS_COLORS.orbisBlue.strong; // '#154194'

// Using helper function
const highlightColor = getOrbisColor('highlight-green-strong'); // '#64a70b'
```

### In SCSS/CSS

```scss
.my-component {
  // Direct color usage
  color: var(--orbis-blue-strong);
  background: var(--orbis-grey-light);
  border-color: var(--solution-petrol-medium);
  
  // With opacity (using RGB values)
  background: rgba(var(--orbis-blue-strong-rgb), 0.1);
  box-shadow: 0 2px 8px rgba(var(--orbis-blue-medium-rgb), 0.2);
}
```

## Available Color Keys

### ORBIS Blue (Primary)
- `orbis-blue-strong` / `--orbis-blue-strong`
- `orbis-blue-medium` / `--orbis-blue-medium`
- `orbis-blue-light` / `--orbis-blue-light`

### ORBIS Grey (Neutral)
- `orbis-grey-strong` / `--orbis-grey-strong`
- `orbis-grey-medium` / `--orbis-grey-medium`
- `orbis-grey-light` / `--orbis-grey-light`

### ORBIS Special Colors
- `orbis-nightblue` / `--orbis-nightblue`
- `orbis-darkgrey` / `--orbis-darkgrey`

### SAP Blue
- `sap-blue-strong` / `--sap-blue-strong`
- `sap-blue-medium` / `--sap-blue-medium`
- `sap-blue-light` / `--sap-blue-light`

### Microsoft Orange
- `microsoft-orange-strong` / `--microsoft-orange-strong`
- `microsoft-orange-medium` / `--microsoft-orange-medium`
- `microsoft-orange-light` / `--microsoft-orange-light`

### Solution Petrol
- `solution-petrol-strong` / `--solution-petrol-strong`
- `solution-petrol-medium` / `--solution-petrol-medium`
- `solution-petrol-light` / `--solution-petrol-light`

### Highlight Green
- `highlight-green-strong` / `--highlight-green-strong`
- `highlight-green-medium` / `--highlight-green-medium`
- `highlight-green-light` / `--highlight-green-light`

### Neutral Colors
- `neutral-darkgrey` / `--neutral-darkgrey`
- `neutral-lightgrey` / `--neutral-lightgrey`

## RGB Values for Opacity

All colors also have corresponding RGB variables (suffix `-rgb`) for use with opacity:

```scss
// Example: 10% opacity blue background
background: rgba(var(--orbis-blue-strong-rgb), 0.1);
```

## Color Specifications

All colors are based on the official ORBIS Corporate Identity Style Guide and include:
- Pantone Solid Coated references
- CMYK values
- RGB values
- HEX values

## Migration Guide

When migrating existing hardcoded colors to the palette:

1. **Identify color usage**: Search for hardcoded HEX values in SCSS files
2. **Map to palette**: Find the closest matching color in the ORBIS palette
3. **Replace**: Use CSS variables instead of hardcoded values
4. **Test**: Verify visual consistency after migration

Example migration:
```scss
// Before
.my-element {
  color: #1f54b2;
  background: rgba(31, 84, 178, 0.1);
}

// After
.my-element {
  color: var(--orbis-blue-strong);
  background: rgba(var(--orbis-blue-strong-rgb), 0.1);
}
```

