# fullstack_developer_capstone — BestCars Dealership Reviews

Project name: **fullstack_developer_capstone**.
Repository name: **xrwvm-fullstack_developer_capstone**.
Application name: **BestCars**.

IBM Full Stack Application Development Capstone, based on the official starter repository. Implementation prepared with AI assistance; review and understand the code before using it in an assessed submission.

## Features

Browse seeded dealerships, filter by state, view customer reviews with VADER sentiment, register and log in using Django sessions, and post reviews under the authenticated account. About and Contact pages are under `server/frontend/static`. Django admin manages car makes, models, and users.

## Architecture

React → Django (accounts, SQLite, API gateway) → Express/MongoDB (dealerships/reviews) and Flask/NLTK VADER (sentiment). Seed data comes from the starter dataset. The sentiment lexicon is bundled, so sentiment analysis does not download data at runtime.

## Run with Docker Compose

Requires Docker with Compose. Set `DJANGO_SECRET_KEY` to a stable random value in your shell; never commit it. Then run:

```sh
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000. MongoDB and Django data persist in named volumes. For a cloud hostname set `ALLOWED_HOSTS` to that hostname. Service ports for MongoDB, Express and sentiment are private to the Compose network. Demo contact details and team profiles are illustrative.

## Local development

```sh
python -m venv .venv
.venv/bin/pip install -r server/requirements.txt -r server/djangoapp/microservices/requirements.txt
npm ci --prefix server/frontend
npm run build --prefix server/frontend
npm ci --prefix server/database
.venv/bin/python server/manage.py migrate
.venv/bin/python server/manage.py seed_cars
```

Start MongoDB locally, then run `npm start --prefix server/database`, `.venv/bin/python server/djangoapp/microservices/app.py`, and `.venv/bin/python server/manage.py runserver 0.0.0.0:8000` in separate terminals. Set a stable `DJANGO_SECRET_KEY` for every Django process. Defaults connect the internal services on localhost ports 3030 and 5050.

## Validation

```sh
.venv/bin/python server/manage.py test djangoapp
(cd server/djangoapp/microservices && ../../../.venv/bin/python -m unittest test_sentiment)
(cd server/database && npm test)
```

Express tests require MongoDB and use disposable test reviews. GitHub Actions provisions MongoDB, builds React, and runs Django, sentiment and API integration checks. A successful build alone does not establish cloud deployment; deployment evidence must come from a running environment.

## Kubernetes deployment

`deploy/kubernetes.json` defines four Deployments and Services plus persistent claims for MongoDB and Django. Build `bestcars-web:local` from `server`, `bestcars-dealers:local` from `server/database`, and `bestcars-sentiment:local` from `server/djangoapp/microservices`; load these images into your cluster or replace their names with your registry images. Create the `bestcars-secrets` Secret with a randomly generated `django-secret` key before applying the manifest. Update the web `ALLOWED_HOSTS` environment value to your actual application hostname. Apply using `kubectl apply -f deploy/kubernetes.json`; use `kubectl port-forward service/bestcars-web 8000:8000` for localhost access.

## Current verification status

React builds successfully. Seven Django tests, three sentiment cases, and two Express/MongoDB integration tests pass. The application was run in the Skills Network lab, and dealership listing, Kansas filtering, and static pages were verified in the browser. Four services are running in the assigned Skills Network Kubernetes namespace. The deployed landing page loads all 50 dealerships. The lab deployment uses disposable pod storage; the base manifest provides persistent-volume claims for a persistent environment. GitHub Actions run #3 completed successfully, including all build and test steps. No claim of a submitted assignment, grade, or certificate is made.

The lab deployment URL is recorded in `docs/verification/deploymentURL.txt`. Lab URLs remain available only while the Skills Network session and port-forward are active. Actual read-only cURL responses are in `docs/verification`. Logged-in browser screenshots and final assessment submission are still pending user review.
