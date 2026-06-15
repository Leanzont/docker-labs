# stage 1
FROM golang:1.26 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# stage 2
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
CMD ["./server"]

