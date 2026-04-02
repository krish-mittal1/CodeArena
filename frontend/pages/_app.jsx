import Head from 'next/head';
import '../src/app.css';
import AppProviders from '../src/next/AppProviders';
import { DEFAULT_DESCRIPTION, SITE_NAME, SITE_URL } from '../src/next/seo';

export default function CodeArenaApp({ Component, pageProps }) {
    return (
        <AppProviders>
            <Head>
                <meta name="application-name" content={SITE_NAME} />
                <meta name="apple-mobile-web-app-title" content={SITE_NAME} />
                <meta name="theme-color" content="#c96d3a" />
                <meta name="format-detection" content="telephone=no" />
                <meta name="description" content={DEFAULT_DESCRIPTION} />
                <meta property="og:site_name" content={SITE_NAME} />
                <meta property="og:locale" content="en_US" />
                <meta name="twitter:site" content="@codexarena" />
                <meta name="twitter:creator" content="@codexarena" />
                <meta property="og:image" content={`${SITE_URL}/logo.svg`} />
            </Head>
            <Component {...pageProps} />
        </AppProviders>
    );
}
