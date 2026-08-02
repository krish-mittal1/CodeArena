import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Legacy /problems hub — CP track removed; send users to DSA practice.
 */
export default function Problems() {
    const navigate = useNavigate();

    useEffect(() => {
        navigate('/practice/dsa', { replace: true });
    }, [navigate]);

    return (
        <div className="min-h-screen bg-bg-root flex items-center justify-center">
            <p className="text-text-secondary text-sm">Opening DSA practice…</p>
        </div>
    );
}
