# Frontend Dockerfile (to be placed in /frontend/Dockerfile)

# Stage 1: Build
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy the frontend directory
COPY frontend/ .

# Accept build argument for VITE_API_BASE_URL
ARG VITE_API_BASE_URL
# Set environment variable for the build step
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Install dependencies
RUN npm ci

# Build the application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]