FROM python:3.9-slim-buster as builder
WORKDIR /tmp
RUN pip install pipenv
COPY Pipfile Pipfile.lock /tmp/
RUN pipenv lock -r > requirements.txt

FROM python:3.9-slim-buster as runner
WORKDIR /user/src/app
COPY --from=builder /tmp/requirements.txt /user/src/app/requirements.txt
# ref: https://github.com/locustio/locust/blob/a0bcd31e3dbed934dccaf6dd33daf16eb96550b6/Dockerfile#L5
RUN apt-get update && apt install -y --no-install-recommends git gcc python3-dev && pip install --no-cache-dir --upgrade -r /user/src/app/requirements.txt
COPY ./locustfile.py /user/src/app/locustfile.py