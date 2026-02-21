/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   useWebSocket — React hook for WebSocket lifecycle
   
   Connects/disconnects based on auth state.
   Registers event handlers on mount, cleans up on unmount.
   Exposes connection state reactively.
   
   Usage: call once in App.jsx (or a top-level provider)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useWsStore } from '../stores/wsStore';
import wsManager from '../ws/WebSocketManager';
import { registerEventHandlers } from '../ws/eventHandlers';
import { getAccessToken } from '../api/client';

export function useWebSocket() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const setStatus = useWsStore((s) => s.setStatus);
    const cleanupRef = useRef(null);

    useEffect(() => {
        if (!isAuthenticated) {
            wsManager.disconnect();
            return;
        }

        // Register event handlers (returns cleanup fn)
        cleanupRef.current = registerEventHandlers();

        // Subscribe to state changes → sync to Zustand
        const unsubState = wsManager.onStateChange((state) => {
            setStatus(state);
        });

        // Connect with current access token
        const token = getAccessToken();
        if (token) {
            wsManager.connect(token);
        }

        // Cleanup on unmount or auth change
        return () => {
            unsubState();
            if (cleanupRef.current) {
                cleanupRef.current();
                cleanupRef.current = null;
            }
        };
    }, [isAuthenticated, setStatus]);

    return wsManager;
}
