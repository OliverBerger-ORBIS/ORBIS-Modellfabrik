# OSF-UI: Serve pre-built static files with nginx
# Build context: project root. App must be built on host first (avoids QEMU/Node issues for ARM cross-build).
# Run: npm run update-version && nx build osf-ui --configuration=production
FROM nginx:alpine
COPY dist/apps/osf-ui/browser /usr/share/nginx/html
COPY deploy/osf-ui/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
