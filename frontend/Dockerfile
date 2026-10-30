# Build the React application.
FROM node:24-alpine AS builder

WORKDIR /app

# Install dependencies from the existing lockfile.
COPY package*.json ./
RUN npm ci

# Configure the production API endpoint.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy source files and compile the frontend.
COPY . .
RUN npm run build

# Production web server.
FROM nginx:alpine

# Copy the Nginx configuration.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the compiled frontend.
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
