#!/bin/sh

# Constrói um pequeno script JS injetado dinamicamente com as vars de sistema local
echo "window.__env__ = {" > /usr/share/nginx/html/env-config.js
echo "  VITE_API_BASE_URL: '${VITE_API_BASE_URL}'" >> /usr/share/nginx/html/env-config.js
echo "};" >> /usr/share/nginx/html/env-config.js

# Exibe o resultado no docker logs pra facilitar seu debug
cat /usr/share/nginx/html/env-config.js

# Restante do ciclo do Nginx...
exec "$@"
