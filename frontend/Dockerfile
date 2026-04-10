# Frontend Dockerfile
FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# React 기본 포트
EXPOSE 3000

CMD ["npm", "start"]
