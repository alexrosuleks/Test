import { Actor, CheerioCrawler, Dataset } from 'scrapely';

const IPIFY = 'https://api.ipify.org?format=json';

const DEFAULTS = {
    proxyHost: 'rp.evomi.com',
    proxyPort: 1000,
    proxyUsername: 'internal_prod_scraper',
    proxyPasswordTemplate: 'cn7LCzbjONWcAaX8Xnw6_country-{country}_session-{session}',
    countries: ['us', 'de'],
    sessionsPerCountry: 1,
    checkPlatformFallback: true,
};

function buildProxyUrl(input, country, session) {
    const password = input.proxyPasswordTemplate
        .replace(/\{country\}/g, country)
        .replace(/\{session\}/g, session);
    return `http://${input.proxyUsername}:${password}@${input.proxyHost}:${input.proxyPort}`;
}

async function fetchIps(proxyConfiguration, url, count) {
    const ips = [];
    const crawler = new CheerioCrawler({
        proxyConfiguration,
        maxConcurrency: 1,
        maxRequestRetries: 2,
        requestHandlerTimeoutSecs: 30,
        async requestHandler({ body }) {
            const text = typeof body === 'string' ? body : body.toString('utf8');
            ips.push(JSON.parse(text).ip);
        },
    });
    await crawler.run(Array.from({ length: count }, () => url));
    return ips;
}

await Actor.main(async () => {
    const input = { ...DEFAULTS, ...((await Actor.getInput()) ?? {}) };
    console.log('[byop-test-js] starting', {
        countries: input.countries,
        sessionsPerCountry: input.sessionsPerCountry,
        proxyHost: `${input.proxyUsername}:***@${input.proxyHost}:${input.proxyPort}`,
    });

    for (const country of input.countries) {
        for (let i = 1; i <= input.sessionsPerCountry; i += 1) {
            const session = `byop${i}`;
            const proxyUrl = buildProxyUrl(input, country, session);
            console.log(`[byo] ${country}/${session} testing Evomi proxy`);

            let ips = [];
            let error = null;
            try {
                const proxyConfiguration = await Actor.createProxyConfiguration({ proxyUrls: [proxyUrl] });
                ips = await fetchIps(proxyConfiguration, IPIFY, 2);
            } catch (e) {
                error = e?.message ?? String(e);
            }

            const sticky = ips.length === 2 && ips[0] === ips[1];
            console.log(`[byo] ${country}/${session}: ips=${JSON.stringify(ips)} sticky=${sticky}${error ? ` error=${error}` : ''}`);
            await Dataset.pushData({ case: 'byo', country, session, ips, sticky, error });
        }
    }

    if (input.checkPlatformFallback) {
        const fallback = await Actor.createProxyConfiguration();
        let ips = [];
        let error = null;
        try {
            ips = await fetchIps(fallback ?? undefined, IPIFY, 1);
        } catch (e) {
            error = e?.message ?? String(e);
        }
        console.log(`[fallback] proxyConfigurationCreated=${!!fallback} ips=${JSON.stringify(ips)}${error ? ` error=${error}` : ''}`);
        await Dataset.pushData({ case: 'platform-fallback', proxyConfigurationCreated: !!fallback, ips, error });
    }

    console.log('[done] check the dataset for results');
});
