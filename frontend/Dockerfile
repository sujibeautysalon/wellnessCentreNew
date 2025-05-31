# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy outer level package.json
COPY package*.json ./

# Copy the inner frontend directory
COPY frontend/ ./frontend/

# Navigate to frontend directory and install dependencies
WORKDIR /app/frontend
RUN npm install

# Build the app
RUN npm run build

# Production stage
FROM nginx:1.25-alpine

COPY --from=build /app/frontend/dist /usr/share/nginx/html
# The nginx config file should be mounted in docker-compose

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
