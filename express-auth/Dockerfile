FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

COPY .env .env

ENV PORT=8000

EXPOSE 8000

CMD ["node", "server.js"]