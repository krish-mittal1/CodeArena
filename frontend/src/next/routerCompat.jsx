import { createContext, useContext, useEffect, useMemo } from 'react';
import NextLink from 'next/link';
import { useRouter } from 'next/router';

const RouterCompatContext = createContext({ params: {}, locationState: null });

export function RouterCompatProvider({ children, params = {}, locationState = null }) {
    const value = useMemo(() => ({ params, locationState }), [params, locationState]);
    return (
        <RouterCompatContext.Provider value={value}>
            {children}
        </RouterCompatContext.Provider>
    );
}

export function useNavigate() {
    const router = useRouter();
    return (to, options = {}) => {
        if (typeof to === 'number') {
            router.back();
            return;
        }
        if (options?.replace) {
            router.replace(to);
            return;
        }
        router.push(to);
    };
}

export function useLocation() {
    const router = useRouter();
    const { locationState } = useContext(RouterCompatContext);
    const asPath = router.asPath || '/';
    const [pathname, search = ''] = asPath.split('?');
    return {
        pathname,
        search: search ? `?${search}` : '',
        hash: '',
        state: locationState,
    };
}

export function useSearchParams() {
    const router = useRouter();
    const asPath = router.asPath || '/';
    const [, search = ''] = asPath.split('?');
    const params = new URLSearchParams(search ? `?${search}` : '');
    const setParams = (next) => {
        const base = asPath.split('?')[0];
        const q = typeof next === 'function' ? next(params) : next;
        const str = q.toString();
        router.push(str ? `${base}?${str}` : base);
    };
    return [params, setParams];
}

export function useParams() {
    const { params } = useContext(RouterCompatContext);
    return params || {};
}

export function Navigate({ to, replace = false }) {
    const router = useRouter();
    useEffect(() => {
        if (replace) router.replace(to);
        else router.push(to);
    }, [router, to, replace]);
    return null;
}

export function Link({ to, href, children, ...props }) {
    const destination = href ?? to ?? '#';
    return (
        <NextLink href={destination} {...props}>
            {children}
        </NextLink>
    );
}

export function NavLink({ to, className, children, onClick, ...props }) {
    const router = useRouter();
    const currentPath = (router.asPath || '/').split('?')[0];
    const isActive = currentPath === to;
    const resolvedClassName = typeof className === 'function' ? className({ isActive }) : className;
    return (
        <Link to={to} className={resolvedClassName} onClick={onClick} {...props}>
            {children}
        </Link>
    );
}
