FROM node:22-alpine AS frontend
WORKDIR /build
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ .
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ .
COPY --from=frontend /build/dist ./frontend/dist
RUN python manage.py collectstatic --noinput && useradd -m appuser && mkdir -p /data && chown -R appuser:appuser /data /app
USER appuser
EXPOSE 8000
CMD ["sh","-c","python manage.py migrate --noinput && python manage.py seed_cars && gunicorn --bind 0.0.0.0:8000 --workers 2 djangoproj.wsgi:application"]
