# Bot Matchmaking Feature Documentation

## Overview

The bot matchmaking feature automatically pairs lonely users with AI bot players when no real players are available. This keeps users engaged even during low-activity periods.

## Features Implemented

### 1. **Bot Player System**
- **8 Pre-configured Bot Users**: `AlphaBot_7`, `CodeNinja_Bot`, `SilverCoder_AI`, `LogicMaster_Bot`, `PythonPro_AI`, `AlgoWizard_Bot`, `SmartSolver_7`, `CyberCoder_AI`
- **Realistic Usernames**: Bots are indistinguishable from real users in the UI
- **Variable ELO Ratings**: Bots have ELO values ranging from 100-800 for realistic matchmaking
- **Persistent Bot Accounts**: Bots are created once and persisted in the database

### 2. **Automatic Fallback Matching**
- **Wait Time Threshold**: Users wait 10-20 seconds for real opponents
- **Bot Pairing**: After 20 seconds with no match, user is automatically paired with a bot
- **ELO-Based Selection**: Bots are selected within ±200 ELO range of the user for fair matches
- **Prevents Starvation**: Users never wait idle in the queue

### 3. **Realistic Bot Behavior**
- **Code Generation**: Bots submit code after 5-25 second random delay
- **Win/Loss Probability**: 50% win rate to behave like real players
- **Solution Quality**: 40% correct solutions, 60% wrong/incomplete for realism
- **Language Support**: Generates Python, C++, Java, and JavaScript solutions
- **Problem-Aware**: Generates code tailored to the problem type

### 4. **Automatic Submission**
- **Background Processing**: Bots automatically submit code without user interaction
- **Smart Delay**: Each bot waits random time before submitting (prevents simultaneous submissions)
- **Integrated Judging**: Bot submissions go through the same judge system as real players
- **Match Completion**: Matches complete fairly based on bot submission results

## Architecture

### Database Changes

**User Model** (`backend/models/user.py`)
- Added `is_bot: Boolean` field to mark bot accounts

**Migration** (`backend/db/migrations/versions/b4c2d5e8f9a1_add_is_bot_to_users.py`)
- Auto-applied on startup to add the `is_bot` column

### New Services

**Bot Service** (`backend/services/bot_service.py`)
```python
# Key functions:
- get_random_bot_for_elo(db, player_elo): Select bot with similar ELO
- create_bot_user(db, username, initial_elo): Create new bot account
- BotCodeGenerator.generate_solution(problem_title, language): Generate bot code
- get_bot_match_outcome(): Determine win/loss for match
```

**Bot Submission Service** (`backend/services/bot_submission_service.py`)
```python
# Key functions:
- check_and_submit_bot_code(db, redis, match_id): Auto-submit code for bots
- process_bot_submissions_for_active_matches(db, redis): Periodic processing
```

### Modified Services

**Matchmaking Service** (`backend/services/matchmaking_service.py`)
- Added bot fallback logic to `process_queue()`
- If player waits > 20 seconds with no real match, they get a bot
- Uses existing `_create_match()` to ensure consistency

**Matchmaking Worker** (`backend/workers/matchmaking_worker.py`)
- Calls `bot_submission_service.process_bot_submissions_for_active_matches()` each cycle
- Ensures bots submit code at the right time

### Configuration

**Constants** (`backend/core/constants.py`)
```python
BOT_WAIT_TIME_MIN = 10  # seconds
BOT_WAIT_TIME_MAX = 20  # seconds
BOT_SUBMISSION_DELAY_MIN = 5  # seconds
BOT_SUBMISSION_DELAY_MAX = 25  # seconds
```

## How It Works

### Matchmaking Flow

```
User clicks "Find Match"
    ↓
Joins matchmaking queue
    ↓
System tries to find real opponent for 10-20 seconds
    ↓
If real opponent found → Create normal match
    ↓
If no real opponent after 20 seconds → Select random bot with similar ELO
    ↓
Create match with bot player
    ↓
Match starts, both players see opponent info
```

### Bot Submission Flow

```
Bot is paired in match (as player1 or player2)
    ↓
Matchmaking worker periodically checks active matches
    ↓
For each match with a bot:
  - Generate random code (40% correct, 60% wrong)
  - Random delay: 5-25 seconds
  - Submit to judge queue
    ↓
Judge worker processes submission normally
    ↓
Results broadcasted to match room
    ↓
Match completes when one player solves or time expires
```

## Usage

### Seeding Bot Users

#### Automatic (Startup)
Bots are automatically created when the application starts:
```
[INFO] Bot users initialized
[INFO] Created bot: AlphaBot_7 with ELO 100
[INFO] Created bot: CodeNinja_Bot with ELO 200
...
```

#### Manual
Run the seed script:
```bash
# Create/update bots
python -m backend.scripts.seed_bots

# Reset bots (delete and recreate)
python -m backend.scripts.seed_bots --reset
```

### Monitoring Bot Activity

Check logs for bot activity:
```
[MATCHMAKING] BOT FALLBACK: Paired user123 (ELO=500) vs CodeNinja_Bot (ELO=600) after 20.5s wait
[BOT] CodeNinja_Bot submitted for match abc123 (submission_id=xyz789)
[JUDGE] Match abc123 completed. Winner: user123
```

## Game Balance

### Fair Matching
- Bots selected within ±200 ELO of player
- 50% win rate ensures no bias
- ELO updates work normally for wins/losses vs bots

### Matchmaking Philosophy
- Bots never replace real matches
- Real players ALWAYS matched first (expanding window)
- Bots only trigger after timeout threshold
- Prevents abuse (users won't intentionally wait for easier bots)

## Frontend Considerations

### User Experience
- Bots appear as normal users in opponent info
- No visual indicator that opponent is a bot
- Same match interface and gameplay
- Users can't tell difference in real-time

### WebSocket Events
Bot matches broadcast the same events:
- `MATCH_FOUND`: Shows bot username, ELO, problem
- `OPPONENT_SUBMITTED`: Bot submission appears naturally
- `MATCH_ENDED`: Includes bot as winner/loser
- Same match timer and UI behavior

## Future Enhancements

### Possible Improvements
1. **Difficulty Adjustment**: Bots with higher win rates at certain ELO ranges
2. **Learning**: Bots improve strategies over matches (store patterns)
3. **Conversation Simulation**: Random comments during match
4. **Custom ELO Ranges**: Configure matchmaking tolerance per region
5. **Bot Retirement**: Retire bots with extreme ELO (< 0 or > 2000)
6. **A/B Testing**: Different bot personalities for engagement testing

## Troubleshooting

### Bots Not Appearing

**Issue**: Users keep waiting without getting matched to bots

**Check**:
1. Verify bots were created: `SELECT * FROM users WHERE is_bot = true;`
2. Check Redis is working (bot logic requires Redis)
3. Verify matchmaking worker is running
4. Check logs for error messages in bot_service

**Solution**:
```bash
# Force recreate bots
python -m backend.scripts.seed_bots --reset
```

### Bots Submitting Incorrectly

**Issue**: Bot submissions have unexpected verdicts

**Note**: This is by design!
- 40% will be ACCEPTED
- 60% will be WRONG_ANSWER or other failures
- This is intentional for realism

**If all botsubmissions fail**:
1. Check sandbox/Docker is working (`test/execute_code.py`)
2. Verify problem has test cases
3. Check judge_service is operational

### Bots Not Submitting

**Issue**: Bots paired but don't submit code

**Check**:
1. Verify `bot_submission_service.process_bot_submissions_for_active_matches()` is being called
2. Check Redis for delay tracking: `redis-cli KEYS "bot:delay:*"`
3. Verify submission queue has capacity
4. Check logs for errors in `bot_submission_service`

**Solution**:
Restart matchmaking worker:
```bash
# Kill existing worker
pkill -f "python -m backend.workers.matchmaking_worker"

# Restart
cd backend && python -m workers.matchmaking_worker
```

## Testing

### Unit Tests

Test bot selection:
```python
async def test_bot_selection():
    bot = await bot_service.get_random_bot_for_elo(db, 500)
    assert bot is not None
    assert abs(bot.elo - 500) <= 200
```

Test bot fallback:
```python
async def test_bot_fallback_after_timeout():
    # User waits > 20 seconds
    # Call process_queue()
    # Verify match created with bot
```

### Manual Testing

1. Start app with low user count
2. Create user account
3. Click "Find Match"
4. Wait 20+ seconds
5. Should be matched with bot
6. Verify match starts normally
7. Check bot submits code automatically
8. Verify match completes

## Performance Considerations

### Database
- Bot lookup: O(log n) with ELO index
- Bot creation: Once per startup
- Minimal additional queries

### Redis
- Bot delay tracking: One key per bot per match (expires in 1 hour)
- Submission tracking: One set per match (expires in 1 hour)
- Negligible overhead

### Computation
- Code generation: String templates, O(1)
- 50% random check: O(1)
- Happens 5-25 seconds after match, not blocking

## Files Changed

```
backend/
├── models/
│   └── user.py (added is_bot field)
├── services/
│   ├── bot_service.py (NEW)
│   ├── bot_submission_service.py (NEW)
│   └── matchmaking_service.py (added bot fallback)
├── scripts/
│   └── seed_bots.py (NEW)
├── workers/
│   └── matchmaking_worker.py (added bot processing)
├── core/
│   └── constants.py (added BOT_* constants)
├── db/migrations/versions/
│   └── b4c2d5e8f9a1_add_is_bot_to_users.py (NEW)
└── main.py (added bot seeding on startup)
```

## Deployment Checklist

- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify bots created on startup
- [ ] Test matchmaking with small user pool
- [ ] Monitor logs for bot activity
- [ ] Verify WebSocket broadcasts work with bots
- [ ] Test bot code execution in sandbox
- [ ] Verify ELO updates with bot matches
- [ ] Check match history includes bot opponents
