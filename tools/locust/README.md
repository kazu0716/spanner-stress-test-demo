# Caution

- Don't open Lucust Web, must access from internal or set Web-Auth

## How to use in local

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

## How to create GKE cluster

```bash
export CLUSTER_NAME=stress-test-demo
# create cluster
$ gcloud container clusters create $CLUSTER_NAME --cluster-version=1.22 --tags=$CLUSTER_NAME --num-nodes=3 --no-enable-autoupgrade --machine-type=n1-standard-1 --zone asia-northeast1-a --network config-admin-vpc
# check exsist cluster
$ kubectl config get-contexts
# delete clusters
$ gcloud container clusters delete $CLUSTER_NAME --zone asia-northeast1-a

# resize cluster
$ gcloud container clusters resize $CLUSTER_NAME --node-pool default-pool --num-nodes x 

# scale deployment
$ kubectl scale deployment locust-worker --replicas=120

# add node pool
$ gcloud container node-pools create master-pool --cluster $CLUSTER_NAME --machine-type e2-highmem-2 --num-nodes 1 --zone asia-northeast1-a
```