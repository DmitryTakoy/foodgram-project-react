# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
COPY ./docs /usr/share/nginx/html/api/docs/

RUN npm run build
CMD cp -r build result_build

