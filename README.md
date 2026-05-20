# SaaS Credit & Feature Management

Phân hệ lõi quản lý Gói dịch vụ (Packages), phân quyền tính năng (**FBAC**) và ví tín dụng (**SaaS Credits**) cho nền tảng SaaS.

## 1. Giới thiệu dự án
Hệ thống giải quyết 3 bài toán chính:
* **Quản lý tài chính:** Ví tín dụng (`Credits`) cho phép người dùng thanh toán dịch vụ.
* **Phân quyền động (FBAC):** Quyền sử dụng công cụ dựa trên tính năng được mở khóa thay vì vai trò (Role) cố định.
* **Tối ưu trải nghiệm:** Tự động đồng bộ số dư Real-time giữa Backend và Frontend.

## 2. Hướng dẫn vận hành

### Yêu cầu
* **Docker** và **Docker Compose v2+**

### Các bước khởi chạy
Hệ thống đã được đóng gói hoàn toàn bằng Docker, bạn chỉ cần thực hiện 2 bước sau:

**Bước 1: Khởi động hạ tầng**
Chạy lệnh sau tại thư mục gốc để khởi động toàn bộ dịch vụ:
```bash
docker compose up -d --build
```

### Lưu ý:

* Hệ thống sẽ tự động thực hiện Auto-Seeding (Khởi tạo tài khoản admin, nạp vũ khí Pentest và các gói Credits mẫu) ngay khi khởi chạy.

* Hệ thống mặc định sử dụng cấu hình an toàn có sẵn. Nếu muốn thay đổi thông số Database hoặc Secret Key, bạn có thể tạo file .env tại thư mục gốc và theo mẫu có sẵn ở trong file .env.example

**Bước 2: sử dụng**
Sau khi Docker khởi chạy thành công, truy cập trình duyệt tại:

* Frontend: http://localhost:5173

* Admin/User: Sử dụng tài khoản admin / Admin123 để trải nghiệm hệ thống.

**Tác giả: Vũ Thiên Trường - Kỹ thuật Phần mềm **
