FROM node:20

WORKDIR /usr/src/app

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /smart_account_api $APP_HOME
COPY .env $APP_HOME/.env

RUN yarn install

RUN yarn build

EXPOSE 7080
CMD ["yarn", "start"]