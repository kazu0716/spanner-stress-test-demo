## Environment values

- local dev environment
  - project name is dummys

```bash
EMULATOR_CONFIG=emulator
SPANNER_EMULATOR_HOST=localhost:9010
GOOGLE_CLOUD_PROJECT=stress-test-demo
INSTANCE_NAME=local
DATABASE_NAME=sample-game
ENV=local
LOG_LEVEL=DEBUG
JSON_LOGS=1
GUNICORN_WORKERS=4
```

- cloud(yaml or json)

```yaml
GOOGLE_CLOUD_PROJECT: XXXXX
INSTANCE_NAME: spanner-demo
DATABASE_NAME: sample-game
ENV: production
LOG_LEVEL: INFO
JSON_LOGS: "1"
GUNICORN_WORKERS: "4"
```


## How to deploy

```bash
export PROJECT_ID=`gcloud config get-value project`
export SERVICENAME=sample-game
export COMMIT_SHA=`git rev-parse --short HEAD`
$ docker build -t gcr.io/$PROJECT_ID/$SERVICENAME:$COMMIT_SHA .
$ docker push gcr.io/$PROJECT_ID/$SERVICENAME:$COMMIT_SHA
$ gcloud run deploy $SERVICENAME --image gcr.io/$PROJECT_ID/$SERVICENAME:$COMMIT_SHA --region asia-northeast1 --port 8000 --env-vars-file .env --concurrency 1000 --allow-unauthenticated
```
