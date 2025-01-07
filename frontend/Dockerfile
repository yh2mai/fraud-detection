# Use an official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json package-lock.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the React app for production
RUN npm run build

# Use Nginx to serve the static files
FROM nginx:stable-alpine

# Copy the build output to the Nginx static directory
COPY --from=0 /app/build /usr/share/nginx/html

# Expose the port Nginx will run on
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
