# Use an official Node.js LTS version (Alpine for smaller image size)
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files separately to leverage Docker caching
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile

# Copy the full frontend source code
COPY . .

# Build the Next.js application
RUN npm run build

# ---- Production Stage ----
FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Copy built files from builder
COPY --from=builder /app/.next .next
COPY --from=builder /app/public public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules node_modules

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_PUBLIC_BACKEND_URL=http://backend:8000

# Expose frontend port
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "run", "start"]