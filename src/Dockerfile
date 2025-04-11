FROM python:3.12

WORKDIR /usr/src/python

ENV PYTHONPATH=/usr/src/python

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
