import Problems from '../src/pages/Problems';
import { RouterCompatProvider } from '../src/next/routerCompat';
import { SEOHead, JsonLd, buildCollectionPageJsonLd } from '../src/next/seo';

export default function ProblemsPage() {
    const title = 'Practice Coding Problems by Track';
    const description =
        'Choose between company-wise DSA practice and Codeforces-style competitive programming on CodeArena.';

    return (
        <>
            <SEOHead
                title={title}
                description={description}
                path="/problems"
                keywords={[
                    'coding problems',
                    'DSA problems',
                    'competitive programming practice',
                    'coding problem sets',
                ]}
            />
            <JsonLd data={buildCollectionPageJsonLd({ title, description, path: '/problems' })} />
            <RouterCompatProvider params={{}}>
                <Problems />
            </RouterCompatProvider>
        </>
    );
}
