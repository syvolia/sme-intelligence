FROM node:20-alpine

WORKDIR /app

# More retries, longer timeouts, and a lower concurrency so a slow network
# doesn't get throttled into a reset.
RUN npm config set fetch-retries 10 \
    && npm config set fetch-retry-factor 5 \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000 \
    && npm config set fetch-timeout 600000 \
    && npm config set maxsockets 5

COPY package*.json ./
RUN npm install --no-audit --no-fund --prefer-offline

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]