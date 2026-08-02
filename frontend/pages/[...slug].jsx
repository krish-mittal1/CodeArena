import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/router';
import Landing from '../src/pages/Landing';
import Login from '../src/pages/Login';
import Register from '../src/pages/Register';
import Dashboard from '../src/pages/Dashboard';
import Battle from '../src/pages/Battle';
import History from '../src/pages/History';
import Profile from '../src/pages/Profile';
import Settings from '../src/pages/Settings';
import Problems from '../src/pages/Problems';
import Practice from '../src/pages/Practice';
import CompanyProblems from '../src/pages/CompanyProblems';
import DsaPracticeHub from '../src/pages/DsaPracticeHub';
import Leaderboard from '../src/pages/Leaderboard';
import Spectate from '../src/pages/Spectate';
import MatchRecap from '../src/pages/MatchRecap';
import Progress from '../src/pages/Progress';
import Insights from '../src/pages/Insights';
import InsightDetail from '../src/pages/InsightDetail';
import InsightShare from '../src/pages/InsightShare';
import StudyPaths from '../src/pages/StudyPaths';
import TopicBrowse from '../src/pages/TopicBrowse';
import MockInterview from '../src/pages/MockInterview';
import { useAuthStore } from '../src/stores/authStore';
import { useBattleStore } from '../src/stores/battleStore';
import { RouterCompatProvider } from '../src/next/routerCompat';
import { SEOHead } from '../src/next/seo';

function LoadingScreen() {
    return (
        <div className="min-h-screen bg-bg-root flex items-center justify-center">
            <div className="text-center">
                <div className="w-14 h-14 mx-auto rounded-xl bg-accent flex items-center justify-center mb-4 animate-pulse">
                    <span className="text-2xl">C</span>
                </div>
                <p className="text-text-secondary text-sm font-medium">Loading CodeArena...</p>
            </div>
        </div>
    );
}

function resolveRoute(slug) {
    if (slug.length === 0) return { kind: 'public', component: Landing, params: {} };
    if (slug.length === 1 && slug[0] === 'login') return { kind: 'publicOnly', component: Login, params: {} };
    if (slug.length === 1 && slug[0] === 'register') return { kind: 'publicOnly', component: Register, params: {} };
    if (slug.length === 1 && slug[0] === 'dashboard') return { kind: 'protected', component: Dashboard, params: {} };
    if (slug.length === 1 && slug[0] === 'history') return { kind: 'protected', component: History, params: {} };
    if (slug.length === 1 && slug[0] === 'leaderboard') return { kind: 'protected', component: Leaderboard, params: {} };
    if (slug.length === 1 && slug[0] === 'progress') return { kind: 'protected', component: Progress, params: {} };
    if (slug.length === 1 && slug[0] === 'insights') return { kind: 'protected', component: Insights, params: {} };
    if (slug.length === 1 && slug[0] === 'study-paths') return { kind: 'protected', component: StudyPaths, params: {} };
    if (slug.length === 1 && slug[0] === 'mock-interview') return { kind: 'protected', component: MockInterview, params: {} };
    if (slug.length === 2 && slug[0] === 'insights') return { kind: 'protected', component: InsightDetail, params: { insightId: slug[1] } };
    if (slug.length === 2 && slug[0] === 'insight') return { kind: 'public', component: InsightShare, params: { shareSlug: slug[1] } };
    if (slug.length === 1 && slug[0] === 'profile') return { kind: 'protected', component: Profile, params: {} };
    if (slug.length === 1 && slug[0] === 'settings') return { kind: 'protected', component: Settings, params: {} };
    if (slug.length === 1 && slug[0] === 'problems') return { kind: 'public', component: Problems, params: {} };
    if (slug.length === 2 && slug[0] === 'practice' && slug[1] === 'dsa') return { kind: 'public', component: DsaPracticeHub, params: {} };
    if (slug.length === 3 && slug[0] === 'practice' && slug[1] === 'dsa' && slug[2] === 'topics') return { kind: 'public', component: TopicBrowse, params: {} };
    if (slug.length === 2 && slug[0] === 'practice' && slug[1] === 'competitive') return { kind: 'redirect', to: '/practice/dsa' };
    if (slug.length === 2 && slug[0] === 'practice') return { kind: 'protected', component: Practice, params: { problemId: slug[1] } };
    if (slug.length === 2 && slug[0] === 'company') return { kind: 'public', component: CompanyProblems, params: { companyId: slug[1] } };
    if (slug.length === 2 && slug[0] === 'battle') return { kind: 'protected', component: Battle, params: { matchId: slug[1] } };
    if (slug.length === 2 && slug[0] === 'spectate') return { kind: 'protected', component: Spectate, params: { matchId: slug[1] } };
    if (slug.length === 2 && slug[0] === 'recap') return { kind: 'public', component: MatchRecap, params: { matchId: slug[1] } };
    return null;
}

export default function CatchAllPage() {
    const router = useRouter();
    const { isAuthenticated, isLoading } = useAuthStore();
    const matchId = useBattleStore((s) => s.matchId);
    const slug = useMemo(() => {
        const raw = router.query.slug;
        if (!raw) return [];
        return Array.isArray(raw) ? raw : [raw];
    }, [router.query.slug]);

    const route = useMemo(() => resolveRoute(slug), [slug]);
    const currentPath = useMemo(() => `/${slug.join('/')}`.replace(/\/+/g, '/'), [slug]);

    useEffect(() => {
        if (!router.isReady || isLoading) return;
        if (!route) {
            router.replace('/');
            return;
        }

        if (route.kind === 'redirect') {
            router.replace(route.to);
            return;
        }

        if (route.kind === 'publicOnly' && isAuthenticated) {
            router.replace(matchId ? `/battle/${matchId}` : '/dashboard');
            return;
        }

        if (route.kind === 'public' && matchId && currentPath === '/') {
            router.replace(`/battle/${matchId}`);
            return;
        }

        if (route.kind === 'protected' && !isAuthenticated) {
            const next = currentPath === '/' ? '/dashboard' : currentPath;
            router.replace(`/login?next=${encodeURIComponent(next)}`);
            return;
        }

        if (
            route.kind === 'protected' &&
            matchId &&
            !currentPath.startsWith('/battle/') &&
            !currentPath.startsWith('/spectate/')
        ) {
            router.replace(`/battle/${matchId}`);
        }
    }, [router, route, isAuthenticated, isLoading, currentPath, matchId]);

    if (!router.isReady || isLoading || !route || route.kind === 'redirect') {
        return <LoadingScreen />;
    }

    if (route.kind === 'publicOnly' && isAuthenticated) {
        return <LoadingScreen />;
    }

    if (route.kind === 'protected' && !isAuthenticated) {
        return <LoadingScreen />;
    }

    if (route.kind === 'protected' && matchId && !currentPath.startsWith('/battle/') && !currentPath.startsWith('/spectate/')) {
        return <LoadingScreen />;
    }

    const Component = route.component;
    return (
        <>
            <SEOHead
                title={
                    slug[0] === 'login' ? 'Login' :
                        slug[0] === 'register' ? 'Register' :
                            slug[0] === 'dashboard' ? 'Dashboard' :
                                slug[0] === 'history' ? 'History' :
                                slug[0] === 'leaderboard' ? 'Leaderboard' :
                                    slug[0] === 'profile' ? 'Profile' :
                                        slug[0] === 'settings' ? 'Settings' :
                                            slug[0] === 'battle' ? 'Live Battle' :
                                                slug[0] === 'spectate' ? 'Spectate' :
                                                    slug[0] === 'recap' ? 'Match Recap' :
                                                        slug[0] === 'practice' ? 'Practice Problem' :
                                                    'CodeArena'
                }
                path={currentPath}
                noindex={route.kind !== 'public'}
            />
            <RouterCompatProvider params={route.params}>
                <Component />
            </RouterCompatProvider>
        </>
    );
}
