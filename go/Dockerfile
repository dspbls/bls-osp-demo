FROM golang:1.17 AS golang
COPY main.go /go
RUN GO111MODULE=auto CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build

FROM alpine:3.15
LABEL maintainer="dspbls"

EXPOSE 5000
COPY --from=golang /go/go /usr/local/bin/

RUN adduser -D web
USER web

CMD [ "/usr/local/bin/go" ]
