#!/bin/bash

case "$1" in
  start)
    echo "🚀 Starting Rasa bot..."
    docker-compose up -d
    ;;
  stop)
    echo "🛑 Stopping Rasa bot..."
    docker-compose down
    ;;
  restart)
    echo "🔁 Restarting Rasa bot..."
    docker-compose down
    docker-compose up -d
    ;;
  *)
    echo "Usage: ./manage.sh {start|stop|restart}"
    exit 1
esac
