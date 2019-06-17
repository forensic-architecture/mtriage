FROM node:lts-alpine as builder
WORKDIR /app
RUN npm install -g yarn
ADD package.json package.json
ADD yarn.lock yarn.lock
RUN yarn install
COPY . .
RUN yarn build

# install nginx to serve the build
FROM nginx
COPY --from=builder /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
