/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   useTimer — local countdown synced with battleStore
   
   Ticks every second while `timerRunning` is true.
   Server syncs handled via battleStore.syncTimer().
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { useEffect, useRef } from 'react';
import { useBattleStore } from '../stores/battleStore';

export function useTimer() {
    const timerRunning = useBattleStore((s) => s.timerRunning);
    const remainingSeconds = useBattleStore((s) => s.remainingSeconds);
    const tickTimer = useBattleStore((s) => s.tickTimer);
    const intervalRef = useRef(null);

    useEffect(() => {
        if (timerRunning && remainingSeconds > 0) {
            intervalRef.current = setInterval(() => tickTimer(), 1000);
        }
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [timerRunning, remainingSeconds > 0, tickTimer]);

    return { remainingSeconds, timerRunning };
}
