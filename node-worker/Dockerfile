FROM node:18-slim AS build

WORKDIR /usr/src/app

COPY package*.json ./

# i dont think we need --production here
RUN npm i

COPY . .

# Second stage: runtime
FROM node:18-slim AS runtime

WORKDIR /usr/src/app

COPY --from=build /usr/src/app ./

# the `start` is defined as `node worker.js` which can be run here as well
CMD ["npm", "start"]
