import { SITE_URL } from '../src/next/seo';

export async function getServerSideProps({ res }) {
    const body = `User-agent: *
Allow: /

Sitemap: ${SITE_URL}/sitemap.xml
`;

    res.setHeader('Content-Type', 'text/plain');
    res.write(body);
    res.end();

    return {
        props: {},
    };
}

export default function Robots() {
    return null;
}
