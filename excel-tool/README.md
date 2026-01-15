# Excel Tool - Django Web Application

Ứng dụng web Django để xử lý file Excel và chuyển đổi sang CSV.

## Yêu cầu hệ thống

- Python >= 3.14
- UV package manager

## Cài đặt

1. Clone hoặc tải project về máy
2. Di chuyển vào thư mục project:
   ```bash
   cd d:\Dev\project\myTool\excel-tool
   ```

3. Cài đặt dependencies:
   ```bash
   uv sync
   ```

## Chạy ứng dụng

### Phương pháp 1: Sử dụng Uvicorn (Khuyến nghị)

**Development mode (với auto-reload):**
```bash
uv run uvicorn mysite.asgi:application --host 0.0.0.0 --port 8000 --reload
```

**Production mode:**
```bash
uv run uvicorn mysite.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

### Phương pháp 2: Sử dụng Django runserver (Development only)

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

## Truy cập ứng dụng

- URL: http://localhost:8000
- Hoặc từ mạng nội bộ: http://[IP-máy-chủ]:8000

## Tính năng

- Upload file Excel (.xls, .xlsx)
- Chuyển đổi Excel sang CSV
- Xử lý encoding tiếng Việt
- Lưu trữ file đã xử lý
- Giao diện web đơn giản

## Cấu trúc thư mục

```
excel-tool/
├── manage.py              # Django management script
├── db.sqlite3            # Database file
├── mysite/               # Django project settings
│   ├── settings.py       # Cấu hình chính
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── tool/                 # Main application
│   ├── views.py         # Business logic
│   ├── urls.py          # App URLs
│   ├── models.py        # Database models
│   ├── forms.py         # Forms
│   └── templates/       # HTML templates
├── media/               # File storage
│   ├── uploads/         # Uploaded files
│   └── outputs/         # Processed files
└── staticfiles/         # Static files (CSS, JS)
```

## Lệnh hữu ích

**Tạo migration:**
```bash
uv run python manage.py makemigrations
```

**Chạy migration:**
```bash
uv run python manage.py migrate
```

**Tạo superuser:**
```bash
uv run python manage.py createsuperuser
```

**Collect static files:**
```bash
uv run python manage.py collectstatic
```

## Khắc phục sự cố

### Lỗi khi truy cập từ mạng nội bộ

1. Kiểm tra Windows Firewall
2. Đảm bảo port 8000 được mở
3. Sử dụng `--host 0.0.0.0` khi chạy server

### Lỗi upload file

1. Kiểm tra quyền thư mục `media/uploads/`
2. Kiểm tra dung lượng file (giới hạn 50MB)

### Lỗi encoding tiếng Việt

- File CSV được lưu với encoding UTF-8-BOM
- Mở bằng Excel hoặc text editor hỗ trợ UTF-8

## Dependencies

- django>=6.0.1
- pandas>=2.3.3  
- xlrd>=2.0.2
- openpyxl>=3.1.5
- uvicorn>=0.40.0

## Ghi chú

- Uvicorn là ASGI server hiệu suất cao, thay thế cho Django runserver
- Hỗ trợ async/await và WebSocket
- Phù hợp cho cả development và production