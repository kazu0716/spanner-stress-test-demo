FROM python:3.9-slim-buster as builder
WORKDIR /tmp
RUN pip install pipenv
COPY Pipfile Pipfile.lock /tmp/
RUN pipenv lock -r > requirements.txt

FROM python:3.9-slim-buster as runner
WORKDIR /user/src/app
COPY --from=builder /tmp/requirements.txt /user/src/app/requirements.txt
RUN apt-get update && apt-get install -y build-essential && pip install --no-cache-dir --upgrade -r /user/src/app/requirements.txt
COPY ./ /user/src/app
ENTRYPOINT python /user/src/app/main.py