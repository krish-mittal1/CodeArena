import { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Eye, Clock, Swords } from 'lucide-react';
import { WS_BASE, WS_EVENTS } from '../utils/constants';
import { getAccessToken } from '../api/client';

function formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function Spectate() {
    const { matchId } = useParams();
    const wsRef = useRef(null);
    const [status, setStatus] = useState('connecting');
    const [room, setRoom] = useState(null);
    const [remaining, setRemaining] = useState(0);
    const [feed, setFeed] = useState([]);
    const [ended, setEnded] = useState(null);

    useEffect(() => {
        const token = getAccessToken();
        if (!token || !matchId) {
            setStatus('error');
            return;
        }

        const url = `${WS_BASE}/ws/spectate/${matchId}?token=${encodeURIComponent(token)}`;
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => setStatus('connected');
        ws.onerror = () => setStatus('error');
        ws.onclose = () => {
            if (status !== 'ended') setStatus('closed');
        };

        ws.onmessage = (evt) => {
            try {
                const msg = JSON.parse(evt.data);
                const event = msg.event;
                const data = msg.data || {};

                if (event === WS_EVENTS.SPECTATOR_JOINED) {
                    setRoom(data);
                    setRemaining(data.remaining_seconds ?? 0);
                }
                if (event === WS_EVENTS.MATCH_TIMER_SYNC) {
                    setRemaining(data.remaining_seconds ?? 0);
                }
                if (event === WS_EVENTS.SUBMISSION_RESULT || event === WS_EVENTS.OPPONENT_SUBMITTED) {
                    setFeed((prev) => [
                        { ts: Date.now(), event, data },
                        ...prev.slice(0, 19),
                    ]);
                }
                if (event === WS_EVENTS.MATCH_ENDED) {
                    setEnded(data);
                    setStatus('ended');
                }
            } catch {
                /* ignore */
            }
        };

        const heartbeat = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ event: WS_EVENTS.HEARTBEAT }));
            }
        }, 30000);

        return () => {
            clearInterval(heartbeat);
            ws.close();
        };
    }, [matchId]);

    useEffect(() => {
        if (status !== 'connected' || remaining <= 0) return;
        const t = setInterval(() => setRemaining((s) => Math.max(0, s - 1)), 1000);
        return () => clearInterval(t);
    }, [status, remaining]);

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root">
            <div className="max-w-2xl mx-auto px-6 py-10">
                <div className="flex items-center gap-3 mb-6">
                    <Eye size={24} className="text-accent" />
                    <div>
                        <h1 className="text-xl font-bold text-text-primary">Spectating</h1>
                        <p className="text-xs text-text-muted font-mono">{matchId}</p>
                    </div>
                </div>

                {status === 'connecting' && (
                    <p className="text-text-secondary text-sm">Connecting to live match...</p>
                )}
                {status === 'error' && (
                    <p className="text-loss text-sm">Could not join as spectator. Match may have ended.</p>
                )}
                {status === 'closed' && !ended && (
                    <p className="text-text-secondary text-sm">Connection closed.</p>
                )}

                {room && (
                    <div className="paper-card grain-panel p-6 mb-6">
                        <h2 className="font-semibold text-text-primary mb-4">{room.problem_title || 'Live match'}</h2>
                        <div className="flex items-center justify-between text-sm text-text-secondary mb-4">
                            <span className="flex items-center gap-2">
                                <Swords size={14} /> Live duel
                            </span>
                            <span className="flex items-center gap-2 font-mono">
                                <Clock size={14} /> {formatTime(remaining)}
                            </span>
                        </div>
                        <p className="text-xs text-text-muted">
                            {room.spectator_count ?? 0} spectator(s) watching
                        </p>
                    </div>
                )}

                {ended && (
                    <div className="paper-card grain-panel p-6 mb-6 border-t-4 border-accent">
                        <p className="font-semibold text-text-primary">Match ended</p>
                        <p className="text-sm text-text-secondary mt-1">
                            Winner: {ended.winner_username || 'Draw'}
                        </p>
                        <Link to={`/recap/${matchId}`} className="text-accent text-sm mt-3 inline-block hover:underline">
                            View recap
                        </Link>
                    </div>
                )}

                {feed.length > 0 && (
                    <div className="paper-card grain-panel p-4">
                        <h3 className="text-xs uppercase tracking-wider text-text-muted mb-3">Live feed</h3>
                        <ul className="space-y-2 text-sm">
                            {feed.map((item) => (
                                <li key={item.ts} className="text-text-secondary border-b border-border/40 pb-2">
                                    {item.event === WS_EVENTS.OPPONENT_SUBMITTED
                                        ? 'A player submitted a solution'
                                        : `Verdict: ${item.data?.verdict || 'update'}`}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
