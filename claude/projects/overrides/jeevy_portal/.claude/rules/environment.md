# Environment Setup

## Backend virtual environment

- **Always activate the backend venv before running Python commands** (black, pytest, pip, python, etc.):
  ```bash
  source /home/_3ntropy/work/jeevy_portal/backend/.venv/bin/activate && black <files>
  ```
- The venv lives at `backend/.venv/` (uv-managed, Python 3.12.2). Shell state does not persist between Bash calls, so source it every time.

## Frontend environment

- **Always set the Node.js PATH before running frontend commands** (npm, npx, next, eslint, etc.):
  ```bash
  PATH="/home/_3ntropy/.nvm/versions/node/v22.13.0/bin:$PATH" && cd /home/_3ntropy/work/jeevy_portal/frontend && npx next build
  ```
- Node v22.13.0 via nvm. Shell state does not persist between Bash calls, so set the PATH every time.
- All frontend commands (`npm install`, `npx next dev`, `npx next lint`, `npx next build`) must run from the `frontend/` directory.

## Formatting

- Format files after making changes (don't wait for commit time — format as you go).
- **Python:** Black (`black .` or the backend format script).
- **JS/TS:** Prettier from the frontend directory: `npx prettier --write <files>`. Config is in `frontend/.prettierrc`. ESLint (`eslint.config.mjs`) has `eslint-config-prettier` to avoid conflicts.
  - Format single files: `npx prettier --write src/path/to/file.js`
  - Format all: `npm run format`
  - Check without writing: `npm run format:check`
