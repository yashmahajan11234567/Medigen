# Frontend Dockerfile - Multi-stage production build

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Accept build-time argument for the API base URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy package files and install dependencies (cached layer)
COPY frontend/package*.json ./
RUN npm ci

# Copy all frontend source code
COPY frontend/ .

# Build the Vite production bundle
RUN npm run build

# Stage 2: Production runtime
FROM nginx:alpine

# Install curl for Docker health checks (nginx:alpine does not include it)
RUN apk add --no-cache curl

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
