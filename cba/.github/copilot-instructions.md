**Purpose**

This file gives actionable, repository-specific guidance for AI coding agents (Copilot-style) to be immediately productive in this Flask-based project.

**Quick Orientation**
- **App entry**: `app.py` — single-file Flask app that also defines the SQLAlchemy models and routes.
- **Config**: `config.py` — reads `DATABASE_URL`, `SECRET_KEY`, and `DEBUG` from environment; `app.py` sometimes uses a hard-coded fallback (`sqlite:///clamping_business.db`).
- **DB & migrations**: lightweight SQLite. One-off migration script: `migrate_db.py`. Startup-time schema tweaks are performed by `ensure_force_password_column()` in `app.py`.
- **Instance DB path**: `instance/clamping_business.db` is used by some scripts; the app also supports `clamping_business.db` at repo root.
- **Templates & static**: UI lives in `templates/` and `static/` (PWA assets like `static/manifest.json` are exercised by tests).

**What to change vs what to avoid**
- Prefer minimal edits to `app.py` structure; many routes and models live there. If extracting code, keep the app context behavior identical (the module creates `app`, calls `db.create_all()` and runs `app.run()` under `if __name__ == '__main__'`).
- Do not commit a plaintext `SECRET_KEY` or production `DEFAULT_ADMIN_PASSWORD`; use `env` variables. `app.py` will create an insecure default admin account if `DEFAULT_ADMIN_PASSWORD` is not set — document or avoid altering that behavior without explicitly implementing a safer provisioning flow.

**Common development workflows**
- Run locally: `source venv/bin/activate` then `python app.py`. The app binds to `0.0.0.0` by default when run directly.
- Install deps: `pip install -r requirements.txt` (project uses Flask 2.x and Flask-SQLAlchemy 2.5.x per `requirements.txt`).
- Run tests: use `pytest`. The repo has `tests/test_manifest.py` which checks `static/manifest.json`.
- One-time DB column migration: `python migrate_db.py` (operates on `instance/clamping_business.db`); `app.py` will also try to add missing columns at startup with `ensure_force_password_column()`.

**Patterns & project-specific conventions**
- Authentication: session-based auth. `app.py` defines `login_required` and `admin_required` decorators and enforces login globally via `@app.before_request` with a small whitelist (`login`, `static`, `service_worker`). When adding routes, ensure they either are on the whitelist or honor the session login flow.
- Model placement: models are declared in `app.py` (classes `ClampData`, `Appeal`, `User`). Note there is also a `models.py` file that defines a different `db` and a `Clamp` model — this appears unused by the running `app.py`. When changing models, search for both locations to avoid confusion.
- DB column additions: migration approach is pragmatic — plain SQLite `ALTER TABLE` calls. Keep changes backward-compatible and idempotent (see `ensure_force_password_column()` and `migrate_db.py`).
- Templates reference specific route names or `service_worker` endpoint; maintain those function names or update templates accordingly.

**Integration points & external dependencies**
- SQLite via SQLAlchemy (local file-based DB). Environment override via `DATABASE_URL` is supported.
- Werkzeug for password hashing. Admin user creation uses `DEFAULT_ADMIN_PASSWORD` env var if set.
- Static PWA assets: `static/manifest.json` and `static/service-worker.js` — tests validate the manifest schema.

**Examples to reference when coding**
- Add a new authenticated route: follow the `@login_required` pattern, return `render_template('...')`, and ensure template exists (`templates/`). See `index()` and `dashboard()` in `app.py`.
- Update a model safely: use the same style as `ensure_force_password_column()` — check `PRAGMA table_info` then `ALTER TABLE` only if column is missing. See `migrate_db.py` for a dedicated example.
- AJAX endpoint pattern: `@app.route('/api/clamp/<int:id>/amount', methods=['POST'])` returns JSON and updates the DB; follow this pattern for other API-like endpoints.

**Where to look for surprises / gotchas**
- Duplicate `db` definitions: `app.py` does `db = SQLAlchemy(app)` while `models.py` creates `db = SQLAlchemy()` (factory style). Confirm which is used before refactoring.
- Multiple DB file locations: `app.config['SQLALCHEMY_DATABASE_URI']` vs `instance/clamping_business.db` vs root `clamping_business.db`. Migration and script tools try multiple locations.
- `ensure_force_password_column()` prints, swallows certain exceptions, and returns early after a successful migration — use it as the canonical lightweight migration approach.

**When in doubt**
- Run the app locally (`python app.py`) and exercise the UI pages referenced in `templates/` to validate changes.
- For DB changes, test `migrate_db.py` on a copy of the DB and follow the same PRAGMA-check pattern.

If anything is unclear or you want the instructions expanded (examples for common edits, recommended tests to add, or a short contributor checklist), tell me which area to focus on and I'll iterate.
