FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application for production
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Install serve to serve the static files
RUN npm install -g serve

# Copy the build from the build stage
COPY --from=build /app/dist /app/dist

# Expose port
EXPOSE ${PORT:-5173}

# Serve the static files
CMD ["serve", "-s", "dist", "-l", "${PORT:-5173}"]
