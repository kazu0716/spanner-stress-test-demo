# How to use in local

```zsh
# you have to create .env ref .env_sample
$ source .env
$ docker-compose build --no-cache
$ docker-compose up -d --scale worker=4
```