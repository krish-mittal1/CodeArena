# SECURITY FIXES - DEPLOYMENT CHECKLIST

## Pre-Deployment

- [ ] Read SECURITY_FIXES_REPORT.md
- [ ] Backup database before migration
- [ ] Update .env with secure JWT_SECRET_KEY (32+ chars)
- [ ] Verify all environment variables are set
- [ ] Run local tests to verify functionality

## Database Migration

```bash
# Run Alembic migration to add is_admin column
alembic upgrade head

# Verify migration succeeded
psql -U postgres -d codearena -c "SELECT * FROM information_schema.columns WHERE table_name='users';"
# Should show is_admin column with type boolean, default false
```

## Configuration Updates

### Required Changes in `.env`

```bash
# CRITICAL: Change JWT secret (use: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=<your-secure-32-char-key-here>

# Already default to secure values - verify in .env:
SPECTATOR_REQUIRE_AUTH=true
MATCH_ACCESS_STRICT=true

# Verify CORS is proper:
# CORS_ORIGINS should NOT contain "*" or regex patterns
```

### Verify Configuration

```bash
# After setting .env, test app starts:
python -c "from backend.config import settings; print('✓ Config valid')"
```

## Application Testing

### Unit Tests to Run

```bash
# Test imports work
pytest backend/core/room_code_rate_limit.py -v
pytest backend/core/secure_logging.py -v
pytest backend/core/timing_safe.py -v

# Test that admin dependency works
pytest backend/dependencies.py -v

# Test OTP rate limiting
pytest backend/services/otp_service.py -v

# Run full test suite
pytest backend/ -v
```

### Manual Security Testing

#### 1. Spectator Authentication
```bash
# Should FAIL without token (now requires auth)
wscat -c 'ws://localhost:8000/ws/spectate/550e8400-e29b-41d4-a716-446655440000'
# Should get: code 4001 "Authentication required"

# Should SUCCEED with token
wscat -c 'ws://localhost:8000/ws/spectate/550e8400-e29b-41d4-a716-446655440000?token=<valid-jwt>'
```

#### 2. Private Room Code Rate Limiting
```bash
# Run from bash - attempt 25 requests rapidly (limit is 20/min)
for i in {1..25}; do
  curl -X POST http://localhost:8000/api/v1/matchmaking/private/join \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"code": "ABC123"}'
done
# After 20 requests, should get 429 Too Many Requests
```

#### 3. Admin-Only Problem Creation
```bash
# Regular user attempts to create problem (should fail)
curl -X POST http://localhost:8000/api/v1/problems \
  -H "Authorization: Bearer <regular-user-token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
# Should get 403 Forbidden

# Admin user creates problem (should succeed)
curl -X POST http://localhost:8000/api/v1/problems \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
# Should get 201 Created
```

#### 4. OTP Rate Limiting
```bash
# Generate multiple OTP requests quickly
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/auth/request-otp \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}' \
    -w "\n%{http_code}\n"
done
# Requests 1-2 should be 200 OK
# After 5th minute or exponential backoff, should get 429 Too Many Requests
```

#### 5. Match Authorization
```bash
# Non-participant tries to view match (should fail)
curl http://localhost:8000/api/v1/matches/<match_id> \
  -H "Authorization: Bearer <non-participant-token>"
# Should get 403 Forbidden

# Participant views match (should succeed)  
curl http://localhost:8000/api/v1/matches/<match_id> \
  -H "Authorization: Bearer <participant-token>"
# Should get 200 OK with match details
```

#### 6. Code Input Validation
```bash
# Try to submit code with null bytes (should fail)
curl -X POST http://localhost:8000/api/v1/submissions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"match_id": "...", "code": "print(\"test\")\\x00malicious", "language": "python"}'
# Should get 422 Unprocessable Entity (validation error)
```

#### 7. CORS Security Headers
```bash
# Check that security headers are present
curl -I http://localhost:8000/api/v1/health
# Should include:
# Strict-Transport-Security: max-age=31536000
# X-Content-Type-Options: nosniff  
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Referrer-Policy: strict-origin-when-cross-origin
```

## Production Deployment Steps

1. **Code Deployment**
   ```bash
   git commit -am "security: fix 18 vulnerabilities"
   git push origin main
   ```

2. **Database Migration**
   ```bash
   # On production server:
   cd /app/codearena
   alembic upgrade head
   ```

3. **Environment Setup**
   ```bash
   # Update production .env
   nano .env
   
   # Required changes:
   # - JWT_SECRET_KEY (new secure value)
   # - SPECTATOR_REQUIRE_AUTH=true (now required)
   # - Verify CORS_ORIGINS list
   ```

4. **Restart Application**
   ```bash
   # Using systemd:
   systemctl restart codearena
   
   # Using Docker:
   docker-compose restart api
   
   # Verify startup:
   curl http://localhost:8000/health
   ```

5. **Smoke Tests**
   ```bash
   # Run basic functionality tests
   pytest integration_tests/ -v -k "not slow"
   ```

6. **Monitor Logs**
   ```bash
   # Watch for any errors
   tail -f /var/log/codearena/app.log
   
   # Look for successful security features:
   # grep "SECURITY" app.log
   # grep "rate limit" app.log
   ```

## Rollback Plan

If issues occur:

```bash
# 1. Stop application
systemctl stop codearena

# 2. Revert migration (if critical)
alembic downgrade -1

# 3. Revert code
git revert HEAD

# 4. Restart
systemctl start codearena

# 5. Monitor
tail -f /var/log/codearena/app.log
```

## Post-Deployment Verification

- [ ] Application starts without errors
- [ ] All endpoints respond correctly
- [ ] WebSocket connections work (both with and without token as appropriate)
- [ ] Rate limiting blocks excessive requests
- [ ] Admin-only endpoints enforce access control
- [ ] Security headers present in responses
- [ ] No sensitive data in logs
- [ ] Database migration applied successfully
- [ ] Users can still authenticate normally
- [ ] Matches can still be created and joined

## Monitoring & Alerts

Set up alerts for:
- 429 Too Many Requests (rate limiting triggered)
- 403 Forbidden (authorization failures)
- Failed WebSocket connections  
- OTP verification failures (potential brute force)
- Database migration errors

## Documentation Updates

- [ ] Update API documentation for admin endpoints
- [ ] Document new rate limiting in API docs
- [ ] Add security headers to response documentation
- [ ] Document spectator auth requirement
- [ ] Update deployment guides

---

**Status:** Ready for deployment
**Last Updated:** 2026-03-31
**Risk Level:** LOW (comprehensive testing, no breaking API changes)

