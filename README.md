# Push Lead App (Python/FastAPI)

Ứng dụng xử lý Form đăng ký và chuyển tiếp dữ liệu về Salesforce & Telegram, được viết lại từ PHP sang Python (FastAPI).

## Cấu trúc dự án

- `main.py`: Mã nguồn chính (FastAPI).
- `static/`: Giao diện HTML (Form, Success, Error).
- `config.env`: Cấu hình (cần tạo file này từ thông tin thực tế).
- `Dockerfile` & `docker-compose.yml`: Cấu hình Docker.

## Cài đặt & Chạy

### Cách 1: Sử dụng Docker (Khuyên dùng)

1. Đảm bảo bạn đã cài Docker và Docker Compose.
2. Chạy lệnh:
   ```bash
   docker-compose up -d --build
   ```
3. Truy cập: `http://localhost:8000`

### Cách 2: Chạy trực tiếp (Python)

1. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
2. Chạy server:
   ```bash
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Biến môi trường (`config.env`)

Tạo file `config.env` với nội dung tương tự:

```env
SF_SALESFORCE_URL=https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8
SF_ORG_ID=...
TG_BOT_TOKEN=...
TG_CHAT_ID=...
...
```
