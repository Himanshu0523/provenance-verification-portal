FROM node:20-alpine

WORKDIR /app

# Install deps first — Docker layer cache survives source edits
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000
ENV NEXT_TELEMETRY_DISABLED=1
CMD ["npm", "run", "dev"]