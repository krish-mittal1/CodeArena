import '../src/app.css';
import AppProviders from '../src/next/AppProviders';

export default function CodeArenaApp({ Component, pageProps }) {
    return (
        <AppProviders>
            <Component {...pageProps} />
        </AppProviders>
    );
}
