FROM python:3-alpine AS builder

WORKDIR /usr/src/app

COPY . .

RUN rm -rf test

FROM python:3-alpine AS runner

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app /usr/src/app

EXPOSE 5050

VOLUME ["/root/.local/share/local-audio-yomichan"]

CMD ["python", "./run_server.py"]
