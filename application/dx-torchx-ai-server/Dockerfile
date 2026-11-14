FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --only=production

COPY dist ./dist

COPY src/test_images ./dist/test_images

CMD ["node", "dist/server.js"]
