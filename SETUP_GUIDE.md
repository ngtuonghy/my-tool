# Excel Tool V2 - Complete Setup Guide

## Project Structure

```
myTool/
├── backend/          # FastAPI Backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Core logic & config
│   │   └── utils/    # Utilities
│   ├── uploads/      # Temp uploads
│   ├── outputs/      # Processed files
│   └── .env          # Backend config
│
└── frontend/         # SvelteKit Frontend
    ├── src/
    │   ├── lib/      # API client & components
    │   └── routes/   # Pages
    └── .env          # Frontend config
```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Run server
uv run uvicorn app.main:app --reload --port 8000
```

**Backend will run at:** http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (if not done)
npm install

# Run dev server
npm run dev
```

**Frontend will run at:** http://localhost:5173

## Environment Configuration

### Backend (.env)

Create `backend/.env` (optional, defaults work for local dev):

```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILES=20
```

### Frontend (.env)

File `frontend/.env` already created with:

```env
PUBLIC_API_BASE_URL=http://localhost:8000/api
```

## Verify Setup

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **API Docs**:
   Open http://localhost:8000/docs

3. **Frontend**:
   Open http://localhost:5173

## Testing the Application

1. Open frontend at http://localhost:5173
2. Upload an Excel file (.xls or .xlsx)
3. Set "Rows to Skip" (default: 8)
4. Click "Process File"

**Single Sheet:**
- File processes automatically
- Download CSV button appears

**Multiple Sheets:**
- Sheet selection appears
- Choose "Download All (ZIP)" or select specific sheets

## Production Deployment

### Backend

```bash
# Build and run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Set environment variables:
- `CORS_ORIGINS` - Add your frontend domain

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

Set environment variable:
- `PUBLIC_API_BASE_URL` - Your backend API URL

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:

1. Check backend is running on port 8000
2. Verify `CORS_ORIGINS` in `backend/app/core/config.py` includes `http://localhost:5173`
3. Restart backend server

### API Connection Failed

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `frontend/.env` has correct `PUBLIC_API_BASE_URL`
3. Restart frontend dev server

### File Upload Errors

1. Check `backend/uploads/` directory exists and is writable
2. Verify file size is under 50MB (configurable in config.py)
3. Check backend logs for detailed error messages

## Features

✅ Single-sheet Excel files - Auto-process and download
✅ Multi-sheet Excel files - Select sheets or download all as ZIP
✅ Drag-and-drop file upload
✅ Skip rows configuration with localStorage persistence
✅ Modern UI with shadcn-svelte components
✅ Loading states and error handling
✅ Responsive design
✅ Type-safe API with TypeScript

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- pandas - Excel/CSV processing
- openpyxl - Excel file reading
- uvicorn - ASGI server
- uv - Fast Python package manager

**Frontend:**
- SvelteKit - Full-stack Svelte framework
- TypeScript - Type safety
- shadcn-svelte - UI components
- Tailwind CSS - Styling
- Vite - Build tool
