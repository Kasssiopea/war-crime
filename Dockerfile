FROM python:3.11

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# translate (poternet Django i18n)
RUN apt-get update \
    && apt-get install -y gettext \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY production-docker-entrypoint.sh .
RUN chmod +x /code/production-docker-entrypoint.sh

COPY api_drf/ ./api_drf/
COPY diap/ ./diap/
COPY DRF_DIAP/ ./DRF_DIAP/
COPY moderator/ ./moderator/
COPY locale ./locale/
COPY templates ./templates/
COPY manage.py .



EXPOSE 8000
CMD ["python", "/code/manage.py", "runserver", "0.0.0.0:8000"]
