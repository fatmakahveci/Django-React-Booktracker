FROM node:26-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --strict-peer-deps --engine-strict
COPY frontend/ .
ENV VITE_API_URL=/api/
RUN npm run build
FROM nginx:stable-alpine
COPY deploy/proxy_params /etc/nginx/proxy_params_booktracker
COPY deploy/no-trusted-gateway.conf /etc/nginx/trusted-gateway.conf
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
