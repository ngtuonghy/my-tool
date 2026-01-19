# Environment Configuration Guide

## Frontend (.env)

Tạo file `.env` trong thư mục `frontend/`:

```env
PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Cách sử dụng:

1. **Development (Local)**:
   ```env
   PUBLIC_API_BASE_URL=http://localhost:8000/api
   ```

2. **Production**:
   ```env
   PUBLIC_API_BASE_URL=https://api.yourdomain.com/api
   ```

### Lưu ý:
- Trong SvelteKit, biến môi trường phải có prefix `PUBLIC_` để expose ra browser
- File `.env` đã được tạo sẵn với giá trị mặc định
- API client sẽ tự động sử dụng giá trị từ `.env`
- Nếu không có `.env`, sẽ fallback về `http://localhost:8000/api`

## Backend

Backend không cần `.env` cho development, nhưng có thể tạo nếu cần:

```env
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILES=20
CORS_ORIGINS=["http://localhost:5173"]
```

## Deployment

### Frontend (Vercel/Netlify)
Thêm environment variable trong dashboard:
- Key: `PUBLIC_API_BASE_URL`
- Value: `https://your-backend-api.com/api`

### Backend (Railway/Render)
Không cần config đặc biệt, chỉ cần expose port 8000
