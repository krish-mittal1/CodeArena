import DsaPracticeHub from '../../src/pages/DsaPracticeHub';
import { RouterCompatProvider } from '../../src/next/routerCompat';
import { SEOHead, JsonLd, buildCollectionPageJsonLd } from '../../src/next/seo';

export default function DsaPracticePage() {
    const title = 'Company-wise DSA Practice';
    const description =
        'Practice interview-style DSA problems by company, topic, and difficulty with hidden tests and AI analysis.';

    return (
        <>
            <SEOHead
                title={title}
                description={description}
                path="/practice/dsa"
                keywords={[
                    'company wise DSA',
                    'coding interview practice',
                    'LeetCode style problems',
                    'DSA by company',
                ]}
            />
            <JsonLd data={buildCollectionPageJsonLd({ title, description, path: '/practice/dsa' })} />
            <RouterCompatProvider params={{}}>
                <DsaPracticeHub />
            </RouterCompatProvider>
        </>
    );
}
