FROM node:22-alpine AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /build/build ./frontend/build
RUN python manage.py collectstatic --noinput
RUN mkdir -p /data && useradd -m app && chown -R app:app /app /data
USER app
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_cars && gunicorn djangoproj.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]
