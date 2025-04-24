FROM python:3-alpine AS builder

WORKDIR /usr/src/app

COPY . .

RUN rm -rf test

FROM python:3-alpine AS runner

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app /usr/src/app

VOLUME ["/usr/src/app/plugin/user_files"]

EXPOSE 5050

CMD ["python", "run_server.py"]