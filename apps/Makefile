# !make

include .env

.PHONY: create.emulator.config
create.emulator.config:
	@gcloud config configurations create $(EMULATOR_CONFIG)
	@gcloud config set auth/disable_credentials true
	@gcloud config set project $(GOOGLE_CLOUD_PROJECT)
	@gcloud config set api_endpoint_overrides/spanner http://localhost:9020/

.PHONY: create.emulator.database
create.emulator.database:
	@gcloud config configurations activate $(EMULATOR_CONFIG)
	@gcloud spanner instances create $(INSTANCE_NAME) --config=emulator-config --description=Emulator --nodes=1
	@gcloud spanner databases create $(DATABASE_NAME) --instance=$(INSTANCE_NAME)

.PHONY: spanner-cli
spanner-cli:
	@docker-compose exec spanner-cli spanner-cli -p $(GOOGLE_CLOUD_PROJECT) -i $(INSTANCE_NAME) -d $(DATABASE_NAME)
