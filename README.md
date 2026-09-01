# BYO Proxy Test Actors

Two minimal actors that verify bring-your-own (Evomi) proxying through the
Scrapely SDKs after the `proxy_configuration` fixes.

- `js/` — Node SDK (`@alexrosulek/scrapely` via the `scrapely` shim), base
  `scrapely/actor-node:22`. If the registry only has the version-suffixed tag,
  change the FROM to `scrapely/actor-node:22-<sdk-version>` (e.g. `22-0.1.17`).
- `py/` — Python SDK (`scrapely`), base `scrapely/actor-python:3.14-0.0.1`.

## What each run does

For every `(country, session)` pair (defaults `us`/`de`, 1 session each):

1. Builds the Evomi proxy URL:
   `http://internal_prod_scraper:cn7LCzbjONWcAaX8Xnw6_country-{country}_session-{session}@rp.evomi.com:1000`
2. Creates a `ProxyConfiguration` with that URL as `proxyUrls`/`proxy_urls`
3. Makes **2 requests** to `https://api.ipify.org?format=json` through it
4. Records exit IPs + session stickiness (same session ⇒ same IP) to the dataset

Then one control case (`platform-fallback`): `createProxyConfiguration()` with
no arguments — on-platform this should return the platform proxy injected via
env (or `null` with the BYOP warning when no credentials are present).

## Input (all optional — defaults shown)

JS actor (camelCase):

```json
{
  "proxyHost": "rp.evomi.com",
  "proxyPort": 1000,
  "proxyUsername": "internal_prod_scraper",
  "proxyPasswordTemplate": "cn7LCzbjONWcAaX8Xnw6_country-{country}_session-{session}",
  "countries": ["us", "de"],
  "sessionsPerCountry": 1,
  "checkPlatformFallback": true
}
```

Python actor (snake_case): same fields as `proxy_host`, `proxy_port`,
`proxy_username`, `proxy_password_template`, `countries`,
`sessions_per_country`, `check_platform_fallback`.

## Expected dataset

- one `case: "byo"` row per country/session — `sticky: true`, `us` and `de`
  rows should show different exit IPs
- one `case: "platform-fallback"` row

## Run

```bash
cd js && scrapely push && scrapely run --wait && scrapely logs
```
