# Netlify Deployment Guide for OMF3 Dashboard

This guide explains how to deploy the OMF3 Angular Dashboard to Netlify for hosting as a static site with mock data.

## Overview

The OMF3 Dashboard can be deployed to Netlify to provide access to colleagues without repository permissions. The application runs in mock mode with local fixtures, providing a fully functional demo environment.

## Build Configuration

A dedicated `netlify` build configuration has been added to the project:

- **Configuration**: `omf3/apps/ccu-ui/project.json` → `netlify`
- **Features**:
  - Output hashing enabled for cache busting
  - Optimization enabled
  - Source maps disabled
  - Base href: `/` (Netlify hosts at root)
  - Runtime i18n loading (no compile-time localization)

## Building for Netlify

```bash
npm run build:netlify
```

This command builds the application using the Nx workspace and outputs to `dist/apps/ccu-ui/browser/`.

The build includes:
- Optimized JavaScript bundles with hash names
- All assets (SVG icons, locale files, mock fixtures)
- `_redirects` file for SPA routing support
- Mock data fixtures from `omf3/testing/fixtures/`

## Deployment Options

### Option 1: Netlify CLI (Recommended)

**Prerequisites:**
```bash
npm install -g netlify-cli
```

**First-time deployment:**
```bash
# Login to Netlify
netlify login

# Build the application
npm run build:netlify

# Deploy to Netlify
netlify deploy --prod --dir=dist/apps/ccu-ui/browser
```

**Subsequent deployments:**
```bash
npm run build:netlify
netlify deploy --prod --dir=dist/apps/ccu-ui/browser
```

### Option 2: Manual Drag & Drop

1. Build the application:
   ```bash
   npm run build:netlify
   ```

2. Go to [Netlify Dashboard](https://app.netlify.com)

3. Click "Add new site" → "Deploy manually"

4. Drag the entire `dist/apps/ccu-ui/browser` directory to the upload area

5. Wait for deployment to complete

## Routing Configuration

The application uses Angular's router for client-side navigation. A `_redirects` file ensures all routes are handled by the Angular router:

```
/*    /index.html   200
```

This file is automatically included in the build output.

## Internationalization (i18n)

The application supports English, German, and French locales with **runtime loading**:

- Locale files are served from `/locale/messages.{locale}.json`
- The application detects locale from the URL path: `/en/`, `/de/`, `/fr/`
- No separate builds per locale are needed
- Default locale is English

## Mock Mode

The application automatically runs in mock mode when deployed to Netlify:

- No MQTT connection is established
- All data is loaded from local fixtures
- Fixtures are located in `/fixtures/` directory
- Mock mode is the default in `EnvironmentService`

Users can still switch between environments (mock/replay/live) in the settings, but replay and live modes will not work on Netlify since WebSocket connections are not available.

## Netlify Free Tier

The free tier is sufficient for testing and demo purposes:

- **Bandwidth**: 100 GB/month (≈10,000-50,000 page views)
- **Build minutes**: 300 minutes/month (not used with manual deployment)
- **Sites**: Unlimited
- **Deployment duration**: Unlimited (site stays online until manually deleted)

## Deployment URL

After deployment, you'll receive a URL like:
- `https://<site-name>.netlify.app`
- Custom domains can be configured (requires DNS setup)

## Verification

After deployment, verify:

1. ✅ Application loads at the Netlify URL
2. ✅ Routing works (navigate to different tabs)
3. ✅ Language switching works (en/de/fr)
4. ✅ Mock data is displayed correctly
5. ✅ All icons and assets load properly

## Troubleshooting

### 404 on page refresh
- Ensure `_redirects` file is present in build output
- Check Netlify dashboard for redirect configuration

### Assets not loading
- Verify `base href="/"` in `index.html`
- Check browser console for 404 errors
- Ensure all assets are in the build output

### Locale files not loading
- Check `/locale/messages.{locale}.json` files are in build output
- Verify runtime i18n loading in browser DevTools

## Notes

- No continuous deployment configured (manual deployment only)
- No Git repository connection visible
- Application is completely static (no backend required)
- Environment settings are stored in browser localStorage
