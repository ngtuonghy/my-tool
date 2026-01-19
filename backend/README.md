# Excel Tool V2 Backend

FastAPI backend for Excel to CSV conversion tool with multi-sheet support.

## Setup

### 1. Install Dependencies

```bash
# Install dependencies with uv
uv sync
```

### 2. Environment Configuration (Optional)

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

Default configuration works for local development with frontend at `http://localhost:5173`.

### 3. Run Development Server

```bash
# Run with uv
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

- `POST /api/v1/upload` - Upload Excel file and detect sheets
- `POST /api/v1/process-sheets` - Process selected sheets
- `POST /api/v1/download-zip` - Download all sheets as ZIP
- `GET /api/v1/download/{filename}` - Download processed file

## Environment Variables

See `.env.example` for all available configuration options:

- `UPLOAD_DIR` - Directory for temporary uploads (default: `uploads`)
- `OUTPUT_DIR` - Directory for processed files (default: `outputs`)
- `MAX_FILES` - Maximum files to keep (default: `20`)
- `CORS_ORIGINS` - Allowed frontend origins (default: `["http://localhost:5173"]`)
- `API_PREFIX` - API route prefix (default: `/api`)

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (SvelteKit dev server)
- `http://localhost:3000` (Alternative port)

To add more origins, update `CORS_ORIGINS` in `.env` or `app/core/config.py`.
