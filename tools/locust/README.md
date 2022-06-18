# How to use in local

```zsh
# you have to create .env ref .env_sample
$ source .env
$ docker-compose build --no-cache
$ docker-compose up -d --scale worker=4
```

## How to push images

```zsh
export PROJECT_ID=`gcloud config get-value project`
export SERVICENAME=locust
export COMMIT_SHA=`git rev-parse --short HEAD`
$ docker build -t gcr.io/$PROJECT_ID/$SERVICENAME:$COMMIT_SHA .
$ docker push gcr.io/$PROJECT_ID/$SERVICENAME:$COMMIT_SHA
```