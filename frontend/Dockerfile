FROM node:18-alpine

WORKDIR /app

# M1/M2 Macでのパフォーマンス最適化
ENV CHOKIDAR_USEPOLLING=true

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]