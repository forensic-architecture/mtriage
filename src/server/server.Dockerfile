FROM golang:latest as builder
WORKDIR ../server
COPY . .
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-w -s" -o /app

FROM ubuntu:18.04
# FROM scratch
COPY . .
COPY --from=builder /app /app
ENTRYPOINT ["/app"]
EXPOSE 8080
