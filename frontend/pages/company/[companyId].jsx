import CompanyProblems from '../../src/pages/CompanyProblems';
import { RouterCompatProvider } from '../../src/next/routerCompat';
import { COMPANIES } from '../../src/utils/companies';
import { SEOHead, JsonLd, buildCollectionPageJsonLd } from '../../src/next/seo';

export default function CompanyProblemsPage({ companyId, companyName }) {
    const title = `${companyName} Coding Interview Questions`;
    const description = `Practice ${companyName} coding interview and online assessment problems with company-mapped DSA topics on CodeArena.`;

    return (
        <>
            <SEOHead
                title={title}
                description={description}
                path={`/company/${companyId}`}
                keywords={[
                    `${companyName} coding questions`,
                    `${companyName} DSA problems`,
                    `${companyName} interview preparation`,
                    'company interview questions',
                ]}
            />
            <JsonLd
                data={buildCollectionPageJsonLd({
                    title,
                    description,
                    path: `/company/${companyId}`,
                })}
            />
            <RouterCompatProvider params={{ companyId }}>
                <CompanyProblems />
            </RouterCompatProvider>
        </>
    );
}

export function getStaticPaths() {
    return {
        paths: COMPANIES.map((company) => ({
            params: { companyId: company.id },
        })),
        fallback: false,
    };
}

export function getStaticProps({ params }) {
    const company = COMPANIES.find((item) => item.id === params.companyId);

    if (!company) {
        return { notFound: true };
    }

    return {
        props: {
            companyId: company.id,
            companyName: company.name,
        },
    };
}
