# Uumpa AI - Log Book

## Local Development Workflow

Log Book currently supports only a single provider which uses [Forgejo](https://forgejo.org/)

To start a local instance for development, set the following in `.env` at the repo root:

```
FORGEJO_LOCAL_DEVELOPMENT_INSTANCE=true
# set to an available port on your machine, it will listen only on localhost
FORGEJO_LOCAL_DEVELOPMENT_INSTANCE_HTTP_PORT=3333
```

Run the following command to initialize the Log book, this is safe to run multiple times:

```
uai logbook init
```
