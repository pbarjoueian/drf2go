FROM nginx:1.25-alpine

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Create directories for static and media files
RUN mkdir -p /app/static /app/media && \
    chown -R nginx:nginx /app/static /app/media

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

