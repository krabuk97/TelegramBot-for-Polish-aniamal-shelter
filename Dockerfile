FROM python

WORKDIR \TelegramBot-for-Polish-aniamal-shelter

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r /app/requirements.txt

COPY . .

CMD ["python", "main.py"]