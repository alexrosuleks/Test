# BYO proxy test actor (Python) — Scrapely Python SDK
# SDK is baked into the prebuilt base image
FROM scrapely/actor-python:3.14-0.0.1

COPY --chown=myuser:myuser main.py scrapely.json ./

CMD ["python", "main.py"]
