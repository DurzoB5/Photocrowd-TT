FROM python:3.8.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE config.settings.local

WORKDIR /

# hadolint ignore=DL3008
RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential --no-install-recommends \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev --no-install-recommends \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Create a django group and user.
RUN addgroup --system django \
  && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install --no-cache-dir poetry==1.1.4 \
  && poetry config virtualenvs.create false \
  && poetry install

COPY ./docker/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint \
  && chmod +x /entrypoint \
  && chown django /entrypoint

COPY ./docker/start /start
RUN sed -i 's/\r$//g' /start \
  && chmod +x /start \
  && chown django /start

# Copy all the code over
COPY --chown=django:django . /app

# Switch to the django user
USER django

WORKDIR /app

CMD ["/start"]
ENTRYPOINT ["/entrypoint"]
