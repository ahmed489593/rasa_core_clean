FROM rasa/rasa:3.6.2

WORKDIR /app
COPY . .

RUN pip install python-telegram-bot

ENTRYPOINT ["bash", "-c"]
CMD ["rasa run actions & rasa run --enable-api --cors '*' --debug"]
