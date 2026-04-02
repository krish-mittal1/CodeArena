import CompetitiveProblems from '../../src/pages/CompetitiveProblems';
import { RouterCompatProvider } from '../../src/next/routerCompat';
import { SEOHead, JsonLd, buildCollectionPageJsonLd } from '../../src/next/seo';

export default function CompetitivePracticePage() {
    const title = 'Competitive Programming Practice by Rating';
    const description =
        'Solve Codeforces-style competitive programming problems by rating with raw stdin/stdout judging on CodeArena.';

    return (
        <>
            <SEOHead
                title={title}
                description={description}
                path="/practice/competitive"
                keywords={[
                    'competitive programming practice',
                    'Codeforces style problems',
                    'CP by rating',
                    'stdin stdout coding problems',
                ]}
            />
            <JsonLd data={buildCollectionPageJsonLd({ title, description, path: '/practice/competitive' })} />
            <RouterCompatProvider params={{}}>
                <CompetitiveProblems />
            </RouterCompatProvider>
        </>
    );
}
