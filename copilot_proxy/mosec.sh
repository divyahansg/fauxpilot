#!/bin/bash

# Start the server in the background, redirecting stderr and stdout to main streams
python mosec_server.py &

# Get the process ID (PID) of the server
SERVER_PID=$!

# Start the reverse proxy
nginx -g "daemon off;" &

# Get the process ID (PID) of the reverse proxy
PROXY_PID=$!

# Wait for the server to start
sleep 5

# Configure the reverse proxy to forward requests to the server
cat > /etc/nginx/nginx.conf <<EOF
worker_processes 1;
events {
  worker_connections 1024;
}

http {
  server {
    listen 5000;

    location / {
      proxy_pass http://localhost:3000;
    }

    location /ready {
      proxy_pass http://$TRITON_HOST:8000/v2/health/ready;
    }
  }
}
EOF

# Restart the reverse proxy for the configuration to take effect
nginx -s reload

# Wait for the termination of the container
trap "kill $SERVER_PID $PROXY_PID" SIGTERM
wait $SERVER_PID