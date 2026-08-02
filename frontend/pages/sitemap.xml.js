import { COMPANIES } from '../src/utils/companies';
import { SITE_URL } from '../src/next/seo';

function buildSitemap() {
    const staticPaths = ['/', '/problems', '/practice/dsa'];
    const urls = [
        ...staticPaths.map((path) => `${SITE_URL}${path === '/' ? '' : path}`),
        ...COMPANIES.map((company) => `${SITE_URL}/company/${company.id}`),
    ];

    const body = urls
        .map((url) => `<url><loc>${url}</loc><changefreq>weekly</changefreq><priority>${url === SITE_URL ? '1.0' : '0.8'}</priority></url>`)
        .join('');

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</urlset>`;
}

export async function getServerSideProps({ res }) {
    res.setHeader('Content-Type', 'text/xml');
    res.write(buildSitemap());
    res.end();

    return {
        props: {},
    };
}

export default function Sitemap() {
    return null;
}
