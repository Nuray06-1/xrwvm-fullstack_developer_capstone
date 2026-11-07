# Best Cars — Full Stack Dealership Portal

A working educational application built from the IBM Skills Network capstone starter. Browse dealerships by state, read reviews with sentiment analysis, register and sign in, and post a review with vehicle and purchase information.

## Architecture

- React interface, built with Vite and served by Django/WhiteNoise.
- Django session authentication, CSRF protection, proxy endpoints, and CarMake/CarModel admin. SQLite stores accounts and car catalogue.
- Express + MongoDB dealership and review service, initialized with the original IBM sample data. Startup does not erase existing reviews.
- Flask + NLTK VADER sentiment service using the lexicon included in the starter.
- Docker Compose runs all four services. GitHub Actions tests Django and builds the production container.

## Run locally

Requires Docker with Compose.

```sh
python3 -c "import secrets; print('DJANGO_SECRET_KEY='+secrets.token_urlsafe(48))" > .env
docker compose up --build -d
```

Open http://localhost:8000. Create an account using **Sign up**. Data persists in named Docker volumes.

```sh
docker compose exec web python manage.py createsuperuser
```

The administrator can manage car makes and models at http://localhost:8000/admin/.

Stop without deleting data: `docker compose down`.

## Services and API examples

| URL | Purpose |
| --- | --- |
| http://localhost:8000/about | About us |
| http://localhost:8000/contact | Contact us |
| http://localhost:3030/fetchDealers | All dealerships |
| http://localhost:3030/fetchDealers/Kansas | Kansas dealerships |
| http://localhost:3030/fetchDealer/1 | Dealer details |
| http://localhost:3030/fetchReviews/dealer/1 | Dealer reviews |
| http://localhost:5050/analyze/Excellent%20service | Sentiment response |
| http://localhost:8000/djangoapp/get_cars | Car catalogue |

The browser accesses the Django API under `/djangoapp/`. Mutating routes require a CSRF token and posting reviews requires authentication. Express and MongoDB are internal services; do not expose them directly to the public internet. Local diagnostic ports bind only to loopback.

## Validation

```sh
cd server
python -m pip install -r requirements.txt
cd frontend && npm ci && npm run build && cd ..
python manage.py test djangoapp
python manage.py check
```

Tests cover account creation, password validation, sign-in/out, CSRF, malformed requests, authenticated review authorship, purchase-date validation, state filtering, and car catalogue responses. The CI workflow also builds the production Docker image. The Flask service uses VADER compound-score thresholds of ±0.05.

## Deployment

The production image is defined by the root Dockerfile. It needs reachable Express and sentiment services, persistent storage for SQLite, and these environment variables:

- `DJANGO_SECRET_KEY`: random private value; never commit it.
- `DEBUG=0`
- `ALLOWED_HOSTS`: comma-separated deployment hostnames.
- `CSRF_TRUSTED_ORIGINS`: comma-separated full HTTPS origins.
- `backend_url` and `sentiment_analyzer_url`: internal service URLs.
- `SQLITE_PATH`: persistent writable file path, default `/app/db.sqlite3`.

Run migrations and `seed_cars` before serving (the image command does this). Use one web replica with SQLite; use a managed SQL database before scaling. The provided Compose deployment is local, not a claim of IBM Cloud or Kubernetes deployment.

## Attribution and project status

Starter and sample data: [IBM Skills Network](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone), Apache-2.0 (original LICENSE retained). Implementation prepared with AI assistance. Contact addresses on the demonstration site use the reserved `.example` domain.

This repository does not by itself certify course completion. Screenshots must show actual runs, and any academic submission must follow the course's AI-use and authorship rules. Cloud deployment and a successful remote CI run should be verified before claiming them.

### Code Engine educational demo

`server/database/Dockerfile.demo` packages MongoDB and the Express API in one
container for the restricted Skills Network Code Engine environment. MongoDB
binds only to the container loopback interface; only HTTP port 3030 is exposed.
Run this demo with exactly one instance. Its database, and the web container's
SQLite database, are ephemeral and reset when their containers are replaced.
This is an educational deployment, not a durable production database setup.
The regular Compose deployment retains data in Docker volumes.

The demo image was built locally and `/fetchDealer/1` returned the seeded dealer.
