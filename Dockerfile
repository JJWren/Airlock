FROM ubuntu:latest
LABEL authors="joshu"

ENTRYPOINT ["top", "-b"]