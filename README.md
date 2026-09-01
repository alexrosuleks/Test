# BYO Proxy Test Actor — Python (Evomi)

Minimal actor that verifies bring-your-own (Evomi) proxying through the
Scrapely Python SDK. Base image: `scrapely/actor-python:3.14-0.0.1`.

Evomi separates parameters with `~`; `_` only joins key and value:
`http://internal_prod_scraper:cn7LCzbjONWcAaX8Xnw6_country-{country}~session-{session}@rp.evomi.com:1000`

## What each run does

For every `(country, session)` pair (defaults `us`/`de`, 1 session each):

1. Builds the Evomi proxy URL:
   `http://internal_prod_scraper:cn7LCzbjONWcAaX8Xnw6_country-{country}~session-{session}@rp.evomi.com:1000`
   (Evomi separates parameters with `~`; `_` only joins key and value)
2. Creates a `ProxyConfiguration` with that URL as `proxyUrls`/`proxy_urls`
3. Makes **2 requests** to `https://api.ipify.org?format=json` through it
4. Records exit IPs + session stickiness (same session ⇒ same IP) to the dataset

Then one control case (`platform-fallback`): `createProxyConfiguration()` with
no arguments — on-platform this should return the platform proxy injected via
env (or `null` with the BYOP warning when no credentials are present).

## Input (all optional — defaults shown, snake_case)

```json
{
  "proxy_host": "rp.evomi.com",
  "proxy_port": 1000,
  "proxy_username": "internal_prod_scraper",
  "proxy_password_template": "cn7LCzbjONWcAaX8Xnw6_country-{country}~session-{session}",
  "countries": ["us", "de"],
  "sessions_per_country": 1,
  "check_platform_fallback": true
}
```

## Expected dataset

- one `case: "byo"` row per country/session — `sticky: true`, `us` and `de`
  rows should show different exit IPs
- one `case: "platform-fallback"` row

## Run

Trigger a build from the repo (plain URL works — actor is at the root),
then run and check logs/dataset.

