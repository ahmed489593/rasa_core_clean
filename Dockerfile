FROM rasa/rasa:3.6.2

WORKDIR /app
COPY . .

USER root
RUN pip install --no-cache-dir --break-system-packages python-telegram-bot
USER 1001

ENTRYPOINT ["bash", "-c"]
CMD ["rasa run actions & rasa run --enable-api --cors '*' --debug"]
