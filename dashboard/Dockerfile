# Estágio 1: Build da aplicação React/Vite
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# O Vite precisa acessar variáveis de ambiente de build caso seja necessário.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Estágio 2: Nginx para servir arquivos estáticos
FROM nginx:alpine

# Copiar os arquivos compilados do React
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar uma configuração customizada do nginx se necessário
# Se usar React Router BrowserHistory precisa fazer redirect pra index.html
RUN echo "server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files \$uri \$uri/ /index.html; \
    } \
}" > /etc/nginx/conf.d/default.conf

# Copiar script e conceder permissão
COPY env.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
