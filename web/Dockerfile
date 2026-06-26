FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM node:22-alpine
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_PUBLIC_API_URL=
ENV API_INTERNAL_URL=http://api:8000
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
