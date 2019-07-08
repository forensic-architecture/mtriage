FROM golang:latest as builder
WORKDIR ../server
COPY . .
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-w -s" -o /prodserver

FROM scratch
# FROM ubuntu
COPY . .
COPY --from=builder /prodserver /prodserver
CMD ["/prodserver", "/workingdir"]
EXPOSE 8080
