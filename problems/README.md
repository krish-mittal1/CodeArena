# Problem packages

Version-controlled problem definitions for CodeArena. Each problem lives in its own folder and is synced into PostgreSQL with a single command.

## Directory layout

```
problems/
  two-sum/
    meta.yaml          # Problem metadata + LeetCode signature
    samples/           # Visible examples (used by Run + UI)
      01.in
      01.out
    tests/             # Hidden tests (used by Submit)
      01.in
      01.out
    generator.py       # Optional bulk hidden test generator
```

## meta.yaml

Required fields:

| Field | Description |
|-------|-------------|
| `slug` | Folder name (kebab-case), e.g. `two-sum` |
| `title` | Display title — used as the DB upsert key |
| `difficulty` | `easy`, `medium`, or `hard` |
| `description` | Problem statement |
| `input_format` | Input specification |
| `output_format` | Output specification |

For **LeetCode-style DSA** problems (function + JSON I/O), also set:

```yaml
method_name: twoSum
parameters:
  - name: nums
    type: int[]
  - name: target
    type: int
return_type: int[]
```

The execution engine **generates drivers at runtime** from these fields — you do not author per-problem driver files.

For **competitive programming** (`problem_type: cp`), omit `method_name` / `parameters` / `return_type` and use raw stdin/stdout in `.in` / `.out` files.

### Optional generator

```yaml
generator:
  count: 500
  seed: 42
```

Requires `generator.py` with:

```python
def generate_cases(*, count: int, seed: int, start_index: int):
    for i in range(count):
        yield {
            "input": "...",
            "expected_output": "...",
            "is_sample": False,
        }
```

## Test file format

- Pair files by stem: `01.in` + `01.out`, `02.in` + `02.out`, …
- **DSA mode**: one JSON value per line in `.in` (one line per parameter); JSON in `.out`
- **CP mode**: raw stdin in `.in`, raw stdout in `.out`

`samples/` → `is_sample=True` (shown in UI, used by Run)  
`tests/` → hidden (used by Submit only)

## Sync commands

From the repo root (with backend env configured):

```bash
# Validate all packages without touching the database
python -m backend.tools.sync_problems --all --dry-run

# Sync every package
python -m backend.tools.sync_problems --all

# Sync one problem
python -m backend.tools.sync_problems --slug two-sum
```

On the VPS (inside the API container or with `.env` loaded):

```bash
cd ~/PROJECT2
docker compose -f docker-compose.backend.yml exec api \
  python -m backend.tools.sync_problems --all
```

Sync is **idempotent** — safe to re-run. Problems are matched by `title` and test cases are replaced.

## Adding a new problem

1. Create `problems/my-problem/meta.yaml`
2. Add `samples/` and `tests/` pairs (and optional `generator.py`)
3. Run `python -m backend.tools.sync_problems --slug my-problem`
4. Open the problem in the app — no redeploy needed for content-only changes

## Legacy seed scripts

`backend/scripts/seed_*.py` still work. New problems should use this package format. Migrate old seeds by converting to a folder under `problems/` and running sync.

## Example packages

| Slug | Description |
|------|-------------|
| `two-sum` | Multi-param JSON input + bulk generator |
| `valid-palindrome` | Single string param |
| `jump-game` | Single array param |
