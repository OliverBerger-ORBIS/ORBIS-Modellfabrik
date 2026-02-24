FROM node:18.17.1-alpine3.18 as builder

RUN apk --no-cache --update add git make clang build-base python3

ENV NODE_ENV=production
WORKDIR /app

COPY ./.git* ./
COPY ./frontend ./
COPY ./common ../common
RUN npm ci --include=dev

RUN npm run build
# Due to usage of @angular/localize, the app is build for all languages.
# Therefore, we need to add add all localized app files to the nginx container.
RUN (cd /app/dist/ff-frontend && gzip -k **/*.js **/*.css) # for nginx gzip_static

# running
FROM nginx:1.25.1-alpine

COPY --from=builder /app/dist/ff-frontend/de /usr/share/nginx/html/de/aps
COPY --from=builder /app/dist/ff-frontend/en /usr/share/nginx/html/en/aps
COPY --from=builder /app/dist/ff-frontend/es /usr/share/nginx/html/es/aps
COPY --from=builder /app/dist/ff-frontend/fr /usr/share/nginx/html/fr/aps
COPY --from=builder /app/dist/ff-frontend/nl /usr/share/nginx/html/nl/aps
COPY --from=builder /app/dist/ff-frontend/pt /usr/share/nginx/html/pt/aps
COPY --from=builder /app/dist/ff-frontend/ru /usr/share/nginx/html/ru/aps
COPY --from=builder /app/src/assets /usr/share/nginx/html/de/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/en/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/es/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/fr/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/nl/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/pt/assets
COPY --from=builder /app/src/assets /usr/share/nginx/html/ru/assets

COPY ./frontend/nginx.prod.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
