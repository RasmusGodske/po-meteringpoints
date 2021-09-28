#!/bin/bash
set -e

echo "Starting Message Bus consumer"

# Apply database migrations
alembic --config=migrations/alembic.ini upgrade head

# Run consumer
python -m meteringpoints_consumer
