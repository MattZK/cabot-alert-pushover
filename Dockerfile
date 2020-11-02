FROM cabotapp/cabot

WORKDIR /code
COPY . .

RUN pip install .
