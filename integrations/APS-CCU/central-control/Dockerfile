#
# Builder
#
FROM node:18.17.1-alpine3.18 as builder

WORKDIR /app

COPY ./central-control ./central-control
COPY ./common ./common

WORKDIR /app/central-control
RUN npm ci
RUN npm run build


#
# Actual image
#
FROM node:18.17.1-alpine3.18

ENV NODE_ENV=production

WORKDIR /app
COPY --from=builder /app/central-control/dist/ ./
COPY --from=builder /app/central-control/static-data ./central-control/static-data
COPY --from=builder /app/central-control/package.json ./
COPY --from=builder /app/central-control/package-lock.json ./

RUN npm ci --omit=dev

USER node

CMD ["node", "central-control/src/index.js"]
