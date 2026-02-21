import { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        console.error('[ErrorBoundary]', error, info);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-bg-root flex items-center justify-center p-6">
                    <div className="max-w-md w-full bg-bg-elevated border border-border rounded-2xl p-8 text-center">
                        <div className="w-16 h-16 mx-auto rounded-2xl bg-loss/10 flex items-center justify-center mb-4">
                            <AlertTriangle size={28} className="text-loss" />
                        </div>
                        <h2 className="text-xl font-bold text-text-primary mb-2">Something went wrong</h2>
                        <p className="text-sm text-text-secondary mb-6">
                            {this.state.error?.message || 'An unexpected error occurred'}
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-xl font-medium transition-colors cursor-pointer"
                        >
                            <RefreshCw size={16} />
                            Reload Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
