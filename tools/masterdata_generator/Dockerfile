FROM python:3.9-slim-buster as runner
WORKDIR /user/src/app
COPY ./ /user/src/app
RUN pip install --no-cache-dir --upgrade -r /user/src/app/requirements.txt