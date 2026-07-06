/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   WebSocket Manager — Singleton connection controller
   
   Lifecycle:
     connect(token)  → opens ws://.../ws?token=JWT
     auto-reconnect  → exponential backoff (1s→2s→4s→8s→16s cap)
     heartbeat       → every 30s to prevent idle disconnect
     disconnect()    → clean close, no reconnect
   
   Event system:
     on(event, fn)   → subscribe (returns unsubscribe fn)
     off(event, fn)  → unsubscribe
   
   All timers/intervals are tracked and cleaned up on disconnect.
   No memory leaks — every listener registration returns a cleanup fn.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { WS_BASE, WS_EVENTS } from '../utils/constants';

// Connection states
export const WS_STATE = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
};

class WebSocketManager {
    constructor() {
        // Connection
        this._ws = null;
        this._token = null;
        this._state = WS_STATE.DISCONNECTED;
        this._intentionalClose = false;
        this._connectId = 0;

        // Reconnection
        this._reconnectAttempt = 0;
        this._maxReconnectAttempts = 50;
        this._maxReconnectDelay = 16000;   // 16s cap
        this._baseReconnectDelay = 1000;   // 1s start
        this._reconnectTimer = null;

        // Heartbeat
        this._heartbeatInterval = null;
        this._heartbeatPeriod = 30000;     // 30s

        // Event listeners: Map<event, Set<callback>>
        this._listeners = new Map();

        // State change listeners (for React hook)
        this._stateListeners = new Set();
    }

    // ━━ Public API ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    /** Current connection state */
    get state() {
        return this._state;
    }

    /** Whether the socket is open and ready */
    get isConnected() {
        return this._state === WS_STATE.CONNECTED;
    }

    /**
     * Connect to the WebSocket server.
     * If already connected with same token, no-op.
     * If connected with different token, reconnects.
     */
    connect(token) {
        if (!token) return;

        // Already connected with same token
        if (this._ws && this._token === token && this._state === WS_STATE.CONNECTED) {
            return;
        }

        // Close existing connection first
        if (this._ws) {
            this._ws.onopen = null;
            this._ws.onmessage = null;
            this._ws.onclose = null;
            this._ws.onerror = null;
            this._ws.close();
            this._ws = null;
        }

        this._cleanup();
        this._token = token;
        this._intentionalClose = false;
        this._reconnectAttempt = 0;
        this._connect();
    }

    /**
     * Intentionally disconnect — no auto-reconnect.
     */
    disconnect() {
        this._intentionalClose = true;
        this._cleanup();

        if (this._ws) {
            this._ws.onopen = null;
            this._ws.onmessage = null;
            this._ws.onclose = null;
            this._ws.onerror = null;
            this._ws.close(1000, 'client_disconnect');
            this._ws = null;
        }

        this._token = null;
        this._setState(WS_STATE.DISCONNECTED);
    }

    /**
     * Subscribe to a WebSocket event.
     * Returns an unsubscribe function (safe for React useEffect cleanup).
     */
    on(event, callback) {
        if (!this._listeners.has(event)) {
            this._listeners.set(event, new Set());
        }
        this._listeners.get(event).add(callback);

        // Return unsubscribe fn — no memory leaks
        return () => this.off(event, callback);
    }

    /**
     * Unsubscribe from a WebSocket event.
     */
    off(event, callback) {
        const listeners = this._listeners.get(event);
        if (listeners) {
            listeners.delete(callback);
            if (listeners.size === 0) {
                this._listeners.delete(event);
            }
        }
    }

    /**
     * Subscribe to connection state changes.
     * Returns unsubscribe function.
     */
    onStateChange(callback) {
        this._stateListeners.add(callback);
        return () => this._stateListeners.delete(callback);
    }

    /**
     * Send a message to the server.
     */
    send(event, data = {}) {
        if (this._ws?.readyState === WebSocket.OPEN) {
            this._ws.send(JSON.stringify({ event, data }));
        }
    }

    // ━━ Internal ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _connect() {
        this._setState(
            this._reconnectAttempt > 0 ? WS_STATE.RECONNECTING : WS_STATE.CONNECTING
        );

        const myConnectId = ++this._connectId;

        try {
            const url = `${WS_BASE}/ws?token=${encodeURIComponent(this._token)}`;
            const ws = new WebSocket(url);
            this._ws = ws;

            ws.onopen = () => {
                if (this._connectId !== myConnectId) return;
                this._handleOpen();
            };
            ws.onmessage = (e) => {
                if (this._connectId !== myConnectId) return;
                this._handleMessage(e);
            };
            ws.onclose = (e) => {
                if (this._connectId !== myConnectId) return;
                this._handleClose(e);
            };
            ws.onerror = () => {};
        } catch (err) {
            console.error('[WS] Connection error:', err);
            this._scheduleReconnect();
        }
    }

    _handleOpen() {
        console.log('[WS] Connected');
        this._reconnectAttempt = 0;
        this._setState(WS_STATE.CONNECTED);
        this._startHeartbeat();
    }

    _handleMessage(event) {
        try {
            const { event: eventType, data } = JSON.parse(event.data);

            if (!eventType) return;

            // Dispatch to listeners
            this._dispatch(eventType, data);
        } catch (err) {
            console.warn('[WS] Failed to parse message:', err);
        }
    }

    _handleClose(event) {
        console.log(`[WS] Closed: code=${event.code} reason=${event.reason}`);
        this._stopHeartbeat();

        if (this._intentionalClose) {
            this._setState(WS_STATE.DISCONNECTED);
            return;
        }

        // Unexpected close → reconnect
        this._scheduleReconnect();
    }

    _dispatch(event, data) {
        const listeners = this._listeners.get(event);
        if (listeners) {
            // Iterate over a copy to avoid mutation during dispatch
            for (const callback of [...listeners]) {
                try {
                    callback(data);
                } catch (err) {
                    console.error(`[WS] Listener error for "${event}":`, err);
                }
            }
        }

        // Also dispatch to wildcard '*' listeners (for debugging/logging)
        const wildcard = this._listeners.get('*');
        if (wildcard) {
            for (const callback of [...wildcard]) {
                try {
                    callback({ event, data });
                } catch (err) {
                    console.error('[WS] Wildcard listener error:', err);
                }
            }
        }
    }

    // ━━ Reconnection ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _scheduleReconnect() {
        if (this._intentionalClose || !this._token) return;
        if (this._reconnectAttempt >= this._maxReconnectAttempts) {
            console.error('[WS] Max reconnect attempts reached, giving up');
            this._setState(WS_STATE.DISCONNECTED);
            return;
        }

        this._setState(WS_STATE.RECONNECTING);

        // Exponential backoff: 1s, 2s, 4s, 8s, 16s (capped)
        const delay = Math.min(
            this._baseReconnectDelay * Math.pow(2, this._reconnectAttempt),
            this._maxReconnectDelay
        );

        console.log(
            `[WS] Reconnecting in ${delay}ms (attempt ${this._reconnectAttempt + 1})`
        );

        this._reconnectTimer = setTimeout(() => {
            this._reconnectAttempt++;
            this._connect();
        }, delay);
    }

    // ━━ Heartbeat ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _startHeartbeat() {
        this._stopHeartbeat();
        this._heartbeatInterval = setInterval(() => {
            this.send(WS_EVENTS.HEARTBEAT);
        }, this._heartbeatPeriod);
    }

    _stopHeartbeat() {
        if (this._heartbeatInterval) {
            clearInterval(this._heartbeatInterval);
            this._heartbeatInterval = null;
        }
    }

    // ━━ State ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _setState(newState) {
        if (this._state === newState) return;
        this._state = newState;

        // Notify state listeners
        for (const callback of this._stateListeners) {
            try {
                callback(newState);
            } catch (err) {
                console.error('[WS] State listener error:', err);
            }
        }
    }

    // ━━ Cleanup ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _cleanup() {
        this._stopHeartbeat();

        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }
    }
}

// Singleton — one connection for the entire app
const wsManager = new WebSocketManager();
export default wsManager;
