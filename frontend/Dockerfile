# Stage 1 — Build
# node:18-slim is EOL (Node 18 EOL April 2025). Use Node 20 on Red Hat UBI.
FROM registry.redhat.io/ubi9/nodejs-20-minimal:latest AS builder
ARG REACT_APP_BACKEND_URL=/api
ARG REACT_APP_CLIENT_VALIDATION=Snowflake
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV REACT_APP_CLIENT_VALIDATION=${REACT_APP_CLIENT_VALIDATION}
RUN npm run build

# Stage 2 — Serve with Red Hat UBI nginx (replaces nginx:alpine — not from trusted registry)
FROM registry.redhat.io/ubi9/nginx-124:latest
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
USER 1001
CMD ["nginx", "-g", "daemon off;"]
