# Netlify Deployment Quick Start

This guide provides a quick start for deploying the OMF3 Dashboard to Netlify.

## Prerequisites

- Node.js and npm installed
- Netlify account (free tier is sufficient)

## Quick Deployment Steps

### 1. Build the Application

```bash
npm run build:netlify
```

This creates an optimized build in `dist/apps/ccu-ui/browser/`.

### 2. Deploy to Netlify

#### Option A: CLI Deployment (Recommended)

```bash
# Install Netlify CLI (one-time)
npm install -g netlify-cli

# Login to Netlify (one-time)
netlify login

# Deploy
netlify deploy --prod --dir=dist/apps/ccu-ui/browser
```

#### Option B: Drag & Drop

1. Go to https://app.netlify.com
2. Click "Add new site" → "Deploy manually"
3. Drag the `dist/apps/ccu-ui/browser` folder to the upload area

## What's Included

The build includes everything needed for Netlify:

- ✅ Optimized JavaScript and CSS bundles
- ✅ SPA routing support via `_redirects` file
- ✅ Mock data fixtures for demo mode
- ✅ i18n locale files (German, French)
- ✅ All assets (icons, images, etc.)

## Expected Result

After deployment, you'll get a URL like:
```
https://<site-name>.netlify.app
```

The application will:
- Load in mock mode with sample data
- Support English, German, and French languages
- Work without any backend or MQTT connection
- Allow navigation between all tabs

## Troubleshooting

**Build fails?**
- Ensure all dependencies are installed: `npm install`
- Clear cache: `npx nx reset`

**Routing doesn't work on Netlify?**
- Check that `_redirects` file is in the build output
- Verify deployment directory is `dist/apps/ccu-ui/browser`

**Assets not loading?**
- Check browser console for errors
- Verify base href is `/` in index.html

## Full Documentation

For detailed documentation, see: `docs/netlify-deployment.md`

## Support

For issues or questions, refer to:
- Netlify documentation: https://docs.netlify.com/
- Angular deployment guide: https://angular.io/guide/deployment
