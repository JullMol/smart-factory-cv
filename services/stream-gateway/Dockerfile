FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /stream-gateway ./cmd/server

FROM alpine:3.19

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /stream-gateway .

ENV HTTP_ADDR=:8080
ENV METRICS_ADDR=:9091
ENV AI_ENGINE_URL=ai-inference:50051
ENV LOG_LEVEL=info
ENV TARGET_FPS=15

EXPOSE 8080 9091

ENTRYPOINT ["./stream-gateway"]
