import Head from 'next/head';

export const SITE_NAME = 'CodeArena';
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://codexarena.app';
export const DEFAULT_DESCRIPTION =
    'Practice company-wise DSA, competitive programming, and coding interview problems with AI analysis, hidden tests, and a real coding arena workflow.';
export const DEFAULT_OG_IMAGE = `${SITE_URL}/logo.svg`;

export function buildCanonicalUrl(path = '/') {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${SITE_URL}${normalizedPath === '/' ? '' : normalizedPath}`;
}

export function buildTitle(title) {
    return title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} | Competitive Coding Arena`;
}

export function JsonLd({ data }) {
    if (!data) return null;
    return (
        <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
        />
    );
}

export function SEOHead({
    title,
    description = DEFAULT_DESCRIPTION,
    path = '/',
    noindex = false,
    type = 'website',
    image = DEFAULT_OG_IMAGE,
    keywords = [],
}) {
    const canonical = buildCanonicalUrl(path);
    const fullTitle = buildTitle(title);
    const robots = noindex ? 'noindex, nofollow' : 'index, follow';

    return (
        <Head>
            <title>{fullTitle}</title>
            <meta name="description" content={description} />
            <meta name="keywords" content={keywords.join(', ')} />
            <meta name="robots" content={robots} />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="canonical" href={canonical} />
            <link rel="icon" href="/logo.svg" type="image/svg+xml" />

            <meta property="og:site_name" content={SITE_NAME} />
            <meta property="og:type" content={type} />
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={description} />
            <meta property="og:url" content={canonical} />
            <meta property="og:image" content={image} />

            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={description} />
            <meta name="twitter:image" content={image} />
        </Head>
    );
}

export function buildWebsiteJsonLd() {
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: SITE_NAME,
        url: SITE_URL,
        description: DEFAULT_DESCRIPTION,
        potentialAction: {
            '@type': 'SearchAction',
            target: `${SITE_URL}/problems`,
            'query-input': 'required name=search_term_string',
        },
    };
}

export function buildOrganizationJsonLd() {
    return {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        name: SITE_NAME,
        url: SITE_URL,
        logo: DEFAULT_OG_IMAGE,
    };
}

export function buildCollectionPageJsonLd({ title, description, path }) {
    return {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: title,
        description,
        url: buildCanonicalUrl(path),
        isPartOf: {
            '@type': 'WebSite',
            name: SITE_NAME,
            url: SITE_URL,
        },
    };
}
