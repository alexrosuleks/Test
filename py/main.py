"""BYO (Evomi) proxy test actor for the Scrapely Python SDK."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from scrapely import Actor, ProxyConfiguration

IPIFY = 'https://api.ipify.org?format=json'

DEFAULTS: Dict[str, Any] = {
    'proxy_host': 'rp.evomi.com',
    'proxy_port': 1000,
    'proxy_username': 'internal_prod_scraper',
    'proxy_password_template': 'cn7LCzbjONWcAaX8Xnw6_country-{country}~session-{session}',
    'countries': ['us', 'de'],
    'sessions_per_country': 1,
    'check_platform_fallback': True,
}


def build_proxy_url(conf: Dict[str, Any], country: str, session: str) -> str:
    password = (
        conf['proxy_password_template']
        .replace('{country}', country)
        .replace('{session}', session)
    )
    return f"http://{conf['proxy_username']}:{password}@{conf['proxy_host']}:{conf['proxy_port']}"


async def fetch_ips(proxy_url: Optional[str], count: int) -> List[str]:
    ips: List[str] = []
    async with httpx.AsyncClient(proxy=proxy_url, timeout=30.0) as client:
        for _ in range(count):
            response = await client.get(IPIFY)
            response.raise_for_status()
            ips.append(response.json()['ip'])
    return ips


async def main() -> None:
    async with Actor:
        conf = {**DEFAULTS, **(await Actor.get_input() or {})}
        print(
            f"[byop-test-py] starting countries={conf['countries']} "
            f"sessions_per_country={conf['sessions_per_country']} "
            f"proxy={conf['proxy_username']}:***@{conf['proxy_host']}:{conf['proxy_port']}"
        )

        for country in conf['countries']:
            for i in range(1, conf['sessions_per_country'] + 1):
                session = f'byop{i}'
                proxy_url = build_proxy_url(conf, country, session)
                print(f'[byo] {country}/{session} testing Evomi proxy')

                ips: List[str] = []
                error = None
                try:
                    # Direct ProxyConfiguration path (the code under test)
                    proxy_config = ProxyConfiguration(proxy_urls=[proxy_url])
                    resolved = proxy_config.new_url()
                    ips = await fetch_ips(resolved, 2)
                except Exception as exc:  # noqa: BLE001
                    error = str(exc)

                sticky = len(ips) == 2 and ips[0] == ips[1]
                print(f'[byo] {country}/{session}: ips={ips} sticky={sticky} error={error}')
                await Actor.push_data(
                    {'case': 'byo', 'country': country, 'session': session, 'ips': ips, 'sticky': sticky, 'error': error}
                )

        if conf['check_platform_fallback']:
            fallback = await Actor.create_proxy_configuration()
            ips = []
            error = None
            try:
                resolved = fallback.new_url() if fallback else None
                ips = await fetch_ips(resolved, 1)
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
            print(f'[fallback] proxy_configuration_created={fallback is not None} ips={ips} error={error}')
            await Actor.push_data(
                {'case': 'platform-fallback', 'proxy_configuration_created': fallback is not None, 'ips': ips, 'error': error}
            )

        print('[done] check the dataset for results')


if __name__ == '__main__':
    asyncio.run(main())
