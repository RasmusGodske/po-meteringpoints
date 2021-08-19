# ett-meteringpoints
MeteringPoints domain

# Docker

    docker build -t meteringpoints:v1 .
    docker run --entrypoint /app/entrypoint_api.sh meteringpoints:v1
    docker run --entrypoint /app/entrypoint_consumer.sh meteringpoints:v1
