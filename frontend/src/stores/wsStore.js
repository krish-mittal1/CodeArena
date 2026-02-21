/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   WebSocket Zustand Store — reactive connection state
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { WS_STATE } from '../ws/WebSocketManager';

export const useWsStore = create((set) => ({
    status: WS_STATE.DISCONNECTED,
    reconnectAttempt: 0,

    setStatus: (status) => set({ status }),
    setReconnectAttempt: (attempt) => set({ reconnectAttempt: attempt }),
}));
