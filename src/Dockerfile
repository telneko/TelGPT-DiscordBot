FROM python:3

WORKDIR /usr/src/python

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
