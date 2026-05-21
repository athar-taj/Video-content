# Zem: Repository Hygiene & Git Guidelines

To maintain a clean, lightweight, and secure repository, Zem enforces strict rules around what files should be tracked by version control (Git). This ensures developers can commit code easily without accidentally checking in massive generated assets, environment secrets, or editor configurations.

---

## 🚫 Git Ignore Rules (`.gitignore`)

The project contains a pre-configured `.gitignore` file that excludes the following types of files:

### 1. Credentials & Secrets
*   **Target**: `.env`, `.env.*`
*   **Why**: These files store sensitive API tokens (OpenAI, Mistral, Reddit), database connection strings, and local keys. Under no circumstances should they be committed to the public or team repository.
*   **Exception**: `.env.example` *is* tracked, as it serves as the template for new installations.

### 2. Generated Media & Cache Assets
*   **Target**: `assets/audio/`, `assets/subtitles/`, `assets/renders/`, `assets/timelines/`, `assets/temp/`, `assets/output/`, `assets/memory/`
*   **Why**: The media engine generates raw audio clips, ASS subtitles, temporary transition footage, and finalized video renders. These are binary files that can quickly bloat the Git history to several gigabytes.
*   **Behavior**: The codebase is designed to automatically detect if these directories are missing and create them programmatically at runtime.

### 3. Log Files
*   **Target**: `logs/`, `*.log`, `worker_stderr.log`, `worker_stdout.log`
*   **Why**: Application runtime logs and background worker stdout/stderr redirections contain highly dynamic data and sometimes sensitive debugging payloads.

### 4. External Binaries & Virtual Environments
*   **Target**: `ffmpeg/`, `.venv/`, `venv/`, `ENV/`, `__pycache__/`, `*.egg-info/`, `build/`, `dist/`
*   **Why**: `FFmpeg` binaries are platform-dependent (Windows `.exe` vs Linux ELF) and heavy. Python packages are managed through `uv.lock` or `pyproject.toml` and should be installed within ignored virtual environments.

---

## 🔑 Environment Configuration (`.env`)

Zem uses **Pydantic Settings** to validate and load configurations. The system configurations are defined in [settings.py](file:///z:/Zem/shared/config/settings.py).

### How to configure:
1.  **Clone the template**:
    ```bash
    cp .env.example .env
    ```
2.  **Edit `.env`** with your local/cloud configurations:
    *   `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql+asyncpg://postgres:postgres@localhost:5432/zem_db`).
    *   `REDIS_URL`: Connection string for Redis (e.g., `redis://localhost:6379/0`).
    *   `ENV`: Set to `development` for local testing to bypass heavy dependencies, or `production` for absolute execution.
    *   Add provider API keys if utilizing premium branches (`OPENAI_API_KEY`, etc.).

> [!NOTE]
> If you add a new configuration variable to the codebase, you must:
> 1. Add it as a typed field in `Settings` class inside [settings.py](file:///z:/Zem/shared/config/settings.py).
> 2. Document a placeholder for it inside `.env.example`.

---

## 🛡️ Git Commit Best Practices

Before submitting a Pull Request or committing changes, run this checklist:

1.  **Run `git status`**:
    Double-check that no unexpected files (especially in `assets/` or `.env`) are listed under "Changes to be committed".
2.  **Avoid checking in templates**:
    If you add mock/test videos or voice presets for verification, place them in the ignored folders or keep them local.
3.  **Validate imports and syntax**:
    Ensure that any changes made can compile and run correctly under the local development mocking fallback, meaning a developer who doesn't have an active OpenAI key can still run `test_langgraph_pipeline.py` with mock settings successfully.
