# Stage 0: prod deps only (no dev deps like biome)
FROM node:20-alpine AS deps
WORKDIR /app
COPY web_4_autodining/package.json web_4_autodining/package-lock.json ./
# Retry npm ci up to 3 times on network errors
RUN set -e; for i in 1 2 3; do npm ci --omit=dev && exit 0 || echo "Attempt $i failed, retrying..."; sleep 5; done; exit 1

# Stage 1: build with dev deps
FROM node:20-alpine AS builder

WORKDIR /app

COPY web_4_autodining/package.json web_4_autodining/package-lock.json ./

# Install dependencies (including dev dependencies needed for building)
# Use npm ci to install exactly what's in package-lock.json (prevents version mismatches)
# Retry npm ci up to 3 times on network errors
RUN set -e; for i in 1 2 3; do npm ci && exit 0 || echo "Attempt $i failed, retrying..."; sleep 5; done; exit 1

COPY web_4_autodining/ .
# Copy original dataset files for fallback
COPY webs_server/initial_data/web_4_autodining/original/restaurants_1.json src/data/original/restaurants_1.json

# Build args for environment flags and API URL
# Build arguments for dynamic versions
ARG ENABLE_DYNAMIC_V1=false
ENV NEXT_PUBLIC_ENABLE_DYNAMIC_V1=$ENABLE_DYNAMIC_V1

ARG ENABLE_DYNAMIC_V2_AI_GENERATE=false
ENV NEXT_PUBLIC_ENABLE_DYNAMIC_V2_AI_GENERATE=$ENABLE_DYNAMIC_V2_AI_GENERATE

ARG ENABLE_DYNAMIC_V2_DB_MODE=false
ENV NEXT_PUBLIC_ENABLE_DYNAMIC_V2_DB_MODE=$ENABLE_DYNAMIC_V2_DB_MODE

ARG ENABLE_DYNAMIC_V3=false
ENV NEXT_PUBLIC_ENABLE_DYNAMIC_V3=$ENABLE_DYNAMIC_V3

ARG ENABLE_DYNAMIC_V4=false
ENV NEXT_PUBLIC_ENABLE_DYNAMIC_V4=$ENABLE_DYNAMIC_V4

ARG API_URL=http://app:8090
ENV API_URL=$API_URL

ARG NEXT_PUBLIC_API_URL=http://localhost:8090
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build arg for Git commit hash (passed from setup.sh)
ARG GIT_COMMIT_HASH=unknown

# Extract version from package.json and combine with Git hash for automatic versioning
# Format: "1.0.0+abc1234" (base version + git hash)
# This ensures each build has a unique version without manual updates
RUN BASE_VERSION=$(node -p "require('./package.json').version") && \
    if [ "$GIT_COMMIT_HASH" != "unknown" ] && [ -n "$GIT_COMMIT_HASH" ]; then \
      WEB_VERSION="${BASE_VERSION}+${GIT_COMMIT_HASH}"; \
    else \
      WEB_VERSION="$BASE_VERSION"; \
    fi && \
    echo "NEXT_PUBLIC_WEB_VERSION=$WEB_VERSION" > .env.local && \
    echo "WEB_VERSION=$WEB_VERSION" >> .env.local && \
    echo "✅ Auto-version: $WEB_VERSION"

# Debug: Print the environment variables
RUN echo "🔍 Build-time ENABLE_DYNAMIC_V1: $ENABLE_DYNAMIC_V1"
RUN echo "🔍 Build-time NEXT_PUBLIC_ENABLE_DYNAMIC_V1: $NEXT_PUBLIC_ENABLE_DYNAMIC_V1"
RUN echo "🔍 Build-time ENABLE_DYNAMIC_V2_DB_MODE: $ENABLE_DYNAMIC_V2_DB_MODE"
RUN echo "🔍 Build-time NEXT_PUBLIC_ENABLE_DYNAMIC_V2_DB_MODE: $NEXT_PUBLIC_ENABLE_DYNAMIC_V2_DB_MODE"

RUN npm run build

# Stage 2: Create the lean production image
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8003
EXPOSE 8003

# Note: NEXT_PUBLIC_* variables are embedded at build time in the .next bundle,
# so they don't need to be set here. They're already in the JavaScript code.

# Copy package files first (npm ci requires package-lock.json)
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json

# Install only production dependencies
RUN npm ci --omit=dev --ignore-scripts

# app artifacts
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

CMD ["npm", "start"]
