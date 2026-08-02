"""
Application-wide enums and constants.
"""

from enum import Enum


# ── Match ─────────────────────────────────────────────────────

class MatchStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ── Submission ────────────────────────────────────────────────

class SubmissionStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TLE = "tle"
    MLE = "mle"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"


class Verdict(str, Enum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TLE = "tle"
    MLE = "mle"
    RUNTIME_ERROR = "runtime_error"


# ── Language ──────────────────────────────────────────────────

class Language(str, Enum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"


# ── Difficulty ────────────────────────────────────────────────

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ── ELO ───────────────────────────────────────────────────────

ELO_DEFAULT = 0
ELO_FLOOR = 0

ELO_K_FACTORS = [
    (30, 40),    # 0–30 matches  → K=40
    (100, 24),   # 31–100 matches → K=24
    (None, 16),  # 100+ matches  → K=16
]


# ── Bot Configuration ─────────────────────────────────────────

BOT_WAIT_TIME_MIN = 10  # Minimum wait time before bot fallback (seconds)
BOT_WAIT_TIME_MAX = 20  # Maximum wait time before bot fallback (seconds)
BOT_SUBMISSION_DELAY_MIN = 5  # Bot submits after random delay (min seconds)
BOT_SUBMISSION_DELAY_MAX = 25  # Bot submits after random delay (max seconds)


# ── WebSocket Events ─────────────────────────────────────────

class WSEvent(str, Enum):
    # Server → Client
    MATCH_FOUND = "match_found"
    ROOM_JOINED = "room_joined"
    MATCH_TIMER_SYNC = "match_timer_sync"
    SUBMISSION_QUEUED = "submission_queued"
    SUBMISSION_RUNNING = "submission_running"
    SUBMISSION_RESULT = "submission_result"
    OPPONENT_SUBMITTED = "opponent_submitted"
    MATCH_ENDED = "match_ended"
    SPECTATOR_UPDATE = "spectator_update"
    SPECTATOR_JOINED = "spectator_joined"
    ERROR = "error"

    # Client → Server
    HEARTBEAT = "heartbeat"
    JOIN_SPECTATE = "join_spectate"
    LEAVE_SPECTATE = "leave_spectate"


# ── Redis Keys ────────────────────────────────────────────────

class RedisKey:
    MATCHMAKING_QUEUE = "matchmaking:queue"
    MATCHMAKING_LOCK = "matchmaking:lock:{user_id}"
    MATCHMAKING_MEMBER = "matchmaking:member:{user_id}"
    MATCHMAKING_CLAIM = "matchmaking:claim:{user_id}"
    MATCHMAKING_GLOBAL_LOCK = "matchmaking:global_lock"
    MATCH_STATE = "match:{match_id}:state"
    MATCH_TIMER = "match:{match_id}:timer"
    SUBMISSION_QUEUE = "submission:queue"
    WS_CHANNEL = "ws:match:{match_id}"
    USER_ACTIVE_MATCH = "user:{user_id}:active_match"

    @classmethod
    def matchmaking_lock(cls, user_id: str) -> str:
        return cls.MATCHMAKING_LOCK.format(user_id=user_id)

    @classmethod
    def matchmaking_member(cls, user_id: str) -> str:
        return cls.MATCHMAKING_MEMBER.format(user_id=user_id)

    @classmethod
    def matchmaking_claim(cls, user_id: str) -> str:
        return cls.MATCHMAKING_CLAIM.format(user_id=user_id)

    @classmethod
    def match_state(cls, match_id: str) -> str:
        return cls.MATCH_STATE.format(match_id=match_id)

    @classmethod
    def match_timer(cls, match_id: str) -> str:
        return cls.MATCH_TIMER.format(match_id=match_id)

    @classmethod
    def ws_channel(cls, match_id: str) -> str:
        return cls.WS_CHANNEL.format(match_id=match_id)

    @classmethod
    def user_active_match(cls, user_id: str) -> str:
        return cls.USER_ACTIVE_MATCH.format(user_id=user_id)
