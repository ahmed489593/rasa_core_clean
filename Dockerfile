FROM rasa/rasa:3.6.2

WORKDIR /app
COPY . .

# نثبت لو تحتاج مكتبات إضافية
# RUN pip install -r requirements.txt

RUN rasa train

ENTRYPOINT ["bash", "-c"]
CMD ["rasa run actions & rasa run --enable-api --cors '*' --debug"]
