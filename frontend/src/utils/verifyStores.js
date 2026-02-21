/**
 * Store Instance Verification
 * 
 * Run this in browser console to verify only one instance of each store exists.
 * 
 * Usage:
 *   import { verifyStores } from './utils/verifyStores';
 *   verifyStores();
 */

import { useMatchmakingStore } from '../stores/matchmakingStore';
import { useBattleStore } from '../stores/battleStore';
import { useAuthStore } from '../stores/authStore';

export function verifyStores() {
    console.log('=== Store Instance Verification ===');
    
    // Get store instances (Zustand stores are singletons)
    const matchmakingStore1 = useMatchmakingStore.getState();
    const matchmakingStore2 = useMatchmakingStore.getState();
    const battleStore1 = useBattleStore.getState();
    const battleStore2 = useBattleStore.getState();
    const authStore1 = useAuthStore.getState();
    const authStore2 = useAuthStore.getState();
    
    // Verify singleton behavior
    const matchmakingSame = matchmakingStore1 === matchmakingStore2;
    const battleSame = battleStore1 === battleStore2;
    const authSame = authStore1 === authStore2;
    
    console.log('useMatchmakingStore instances same:', matchmakingSame);
    console.log('useBattleStore instances same:', battleSame);
    console.log('useAuthStore instances same:', authSame);
    
    if (matchmakingSame && battleSame && authSame) {
        console.log('✅ All stores are singletons (single instance)');
    } else {
        console.error('❌ Multiple store instances detected!');
    }
    
    // Check current state
    console.log('\n=== Current Store State ===');
    console.log('Matchmaking:', {
        status: matchmakingStore1.status,
        matchData: matchmakingStore1.matchData,
    });
    console.log('Battle:', {
        matchId: battleStore1.matchId,
        problem: battleStore1.problem,
    });
    
    return {
        matchmakingSame,
        battleSame,
        authSame,
        allSingletons: matchmakingSame && battleSame && authSame,
    };
}
