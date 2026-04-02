import Landing from '../src/pages/Landing';
import { RouterCompatProvider } from '../src/next/routerCompat';
import {
    SEOHead,
    JsonLd,
    buildOrganizationJsonLd,
    buildWebsiteJsonLd,
} from '../src/next/seo';

export default function HomePage() {
    return (
        <>
            <SEOHead
                title="Competitive Coding Arena for DSA and CP Practice"
                description="Practice company-wise DSA problems, Codeforces-style competitive programming, AI analysis, and real coding battles on CodeArena."
                path="/"
                keywords={[
                    'competitive programming platform',
                    'DSA practice',
                    'Codeforces style practice',
                    'coding interview preparation',
                    'AI analysis for code',
                ]}
            />
            <JsonLd data={buildWebsiteJsonLd()} />
            <JsonLd data={buildOrganizationJsonLd()} />
            <RouterCompatProvider params={{}}>
                <Landing />
            </RouterCompatProvider>
        </>
    );
}
