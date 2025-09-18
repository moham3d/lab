# Backend Dockerfile
FROM node:18-alpine

WORKDIR /usr/src/app

# Set production mode before installing so devDependencies are skipped
ENV NODE_ENV=production

# Install dependencies (use npm install which works without a lockfile).
# If you prefer pnpm, we can switch to installing pnpm and using the pnpm lockfile.
COPY package*.json ./
RUN npm install --omit=dev

# Copy source
COPY . .

# Create uploads directory
RUN mkdir -p uploads

ENV PORT=8004
ENV NODE_ENV=production

EXPOSE 8004

CMD ["node", "server.js"]
