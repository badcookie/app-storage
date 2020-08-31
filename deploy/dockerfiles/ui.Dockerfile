FROM node:10.20.0-jessie

RUN mkdir /ui
WORKDIR /ui
COPY package.json .
COPY yarn.lock .

RUN yarn
COPY . .
RUN yarn build

FROM nginx:1.17.9-alpine

RUN mkdir /var/www /var/www/static
COPY --from=1 /ui/build/ /var/www/static/
