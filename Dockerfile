# =============================================================================
# Offload Security — Documentation Site (Docusaurus)
# =============================================================================
# Multi-stage build: Node.js builds the static site, nginx serves it.
#
# Build:  docker build -t cspm-docs docs-site/
# Run:    docker run -p 4000:80 cspm-docs
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Serve
# ---------------------------------------------------------------------------
FROM nginx:1.25-alpine

RUN apk add --no-cache curl

COPY --from=builder /build/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
