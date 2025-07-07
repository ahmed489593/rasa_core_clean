FROM rasa/rasa:3.6.2

WORKDIR /app

COPY . .

USER root

RUN pip install --no-cache-dir rasa-sdk python-telegram-bot requests

RUN chown -R 1001:1001 /app && chmod -R u+rw /app

USER 1001

ENTRYPOINT ["bash", "-c"]
CMD ["rasa run actions & rasa run --enable-api --cors '*' --debug"]
