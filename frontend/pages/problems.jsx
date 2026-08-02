import Problems from '../src/pages/Problems';
import { RouterCompatProvider } from '../src/next/routerCompat';
import { SEOHead, JsonLd, buildCollectionPageJsonLd } from '../src/next/seo';

export default function ProblemsPage() {
    const title = 'Practice DSA Coding Problems';
    const description =
        'Practice company-wise DSA problems with LeetCode-style judging, AI analysis, and interview topics on CodeArena.';

    return (
        <>
            <SEOHead
                title={title}
                description={description}
                path="/problems"
                keywords={[
                    'coding problems',
                    'DSA problems',
                    'coding interview preparation',
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
