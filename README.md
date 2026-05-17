# SaaS Credit & Feature Management Core API - Kho vũ khí công nghệ

**Author:** Vũ Thiên Trường (Thèn Scu - Pink Hat Hacker)
**Role:** Sinh viên Kỹ thuật Phần mềm (HUIT) / Backend Developer
**Status:** Core Module - In Development

---

## 1. Tổng quan dự án (Project Overview)
Dự án này là phân hệ lõi được thiết kế cho các nền tảng SaaS. Phân hệ tập trung giải quyết ba bài toán chính: quản lý dòng tiền ảo, cấu hình linh hoạt các gói sản phẩm, và kiểm soát quyền truy cập tài nguyên hệ thống theo thời gian thực.

Mục tiêu chính của kiến trúc này là đảm bảo tính toàn vẹn dữ liệu trước các rủi ro tương tranh khi thanh toán, tối ưu hóa tốc độ phản hồi của lớp bảo mật, và giúp hệ thống dễ dàng mở rộng theo mô hình kinh doanh.

---

## 2. Công nghệ sử dụng (Technology Stack)
Hệ thống sử dụng các công nghệ hiện đại, tối ưu cho xử lý đồng thời:
* **FastAPI (Python):** Khai thác cơ chế Asynchronous (Async/Await) để xử lý mượt mà các tác vụ I/O Bound, mang lại hiệu năng tốt hơn các framework đồng bộ.
* **PostgreSQL 15 (Docker):** Đảm bảo chuẩn ACID cho giao dịch tài chính, hỗ trợ cơ chế khóa dòng (Row-level Locking).
* **SQLAlchemy ORM:** Quản lý vòng đời dữ liệu và tối ưu các câu truy vấn phức tạp.
* **Pydantic v2:** Đóng vai trò làm DTO, kiểm duyệt chặt chẽ dữ liệu đầu vào và định hình dữ liệu trả về.

---

## 3. Thiết kế & Tối ưu Database
Lược đồ cơ sở dữ liệu được thiết kế tối giản để hạn chế các lệnh `JOIN` phức tạp, giúp truy vấn nhanh hơn khi hệ thống chịu tải cao.

* **`users`:** Quản lý thông tin định danh và tài chính. Thay vì tách riêng một bảng ví tiền, cột `balance` được gộp thẳng vào bảng này để Middleware lấy số dư nhanh nhất có thể.
* **`packages`:** Định nghĩa các gói dịch vụ (ví dụ: Gói Developer, Gói Enterprise) kèm đơn giá và lượng credit.
* **`features`:** Danh sách các tính năng đặc quyền của hệ thống (ví dụ: Tạo ảnh AI, Quét mã độc).
* **`package_features`:** Bảng trung gian (Many-to-Many) để linh hoạt ghép tính năng vào các gói dịch vụ.
* **`user_features`:** Lưu danh sách tính năng mà user thực sự sở hữu để cấp quyền động.
* **`transactions`:** Lưu lịch sử giao dịch, cộng/trừ credit để dễ dàng đối soát.

---

## 4. Mô hình Bảo mật & Phân quyền
Hệ thống tách biệt rõ ràng giữa Xác thực (Authentication) và Phân quyền (Authorization):

* **Xác thực:** Dự kiến dùng chuẩn mã hóa JWT thông qua Header `Authorization`.
* **Phân quyền (Kiến trúc FBAC):** Thay vì dùng mô hình RBAC (dựa trên Role) truyền thống như các framework Java Spring, dự án chọn kiến trúc Feature-Based Access Control (Phân quyền theo tính năng).

**Tại sao lại chọn FBAC cho nền tảng SaaS?**
1. **Linh hoạt:** Quyền gọi API phụ thuộc vào việc user có mã tính năng đó không và ví còn đủ tiền không.
2. **Dễ mở rộng:** Dễ dàng tạo các gói combo mới hoặc bán lẻ từng tính năng mà không làm rối cấu trúc phân quyền cũ của hệ thống.

---

## 5. Tiến độ phát triển (Milestones)

### Giai đoạn 1: Khởi tạo Hạ tầng & Dữ liệu
* Chạy PostgreSQL qua `docker-compose`, mở port 5432 và cấu hình volume để giữ data.
* Map các model từ SQLAlchemy và dùng `Base.metadata.create_all` để tự động tạo bảng.
* Viết script bơm data mồi để sẵn sàng test hệ thống.

### Giai đoạn 2: Quản lý Gói dịch vụ
* Viết các API RESTful để quản lý gói dịch vụ (`POST /api/packages`, `GET /api/packages`).
* Dùng cấu hình `from_attributes=True` của Pydantic để trả về dữ liệu lồng nhau (gói chứa danh sách tính năng) một cách gọn gàng.

### Giai đoạn 3: Xử lý Giao dịch & Chống gian lận
* Hoàn thiện API mua gói và cộng tiền vào ví (`POST /api/transactions/buy`).
* **Chống Race Condition:** Dùng Pessimistic Locking (`SELECT ... FOR UPDATE`) khóa bản ghi của user khi đang xử lý giao dịch. Việc này chặn đứng lỗi nhân đôi tiền khi user cố tình spam click.
* Viết logic cấp quyền thông minh: Chỉ add những tính năng user chưa có vào bảng trung gian để tránh rác Database.

### Giai đoạn 4: Middleware Phân quyền & Trừ tiền
* Tạo Custom Dependency làm màng lọc bảo vệ các API quan trọng.
* Logic kiểm tra 2 lớp:
    1. **Quyền hạn:** User phải có mã tính năng tương ứng, nếu không trả về lỗi `403 Forbidden`.
    2. **Tài khoản:** Số dư phải lớn hơn hoặc bằng chi phí gọi API, nếu không trả về lỗi `402 Payment Required`. Đủ tiền thì trừ thẳng trong Database rồi mới cho API chạy tiếp.

---

## 6. Các bước tiếp theo (Next Steps)
* [ ] Hoàn thiện API `GET /api/users/me` để user xem profile, số dư và các tính năng đang có.
* [ ] Làm luồng Login/Register thật bằng JWT để thay cho việc hardcode `user_id`.
* [ ] Dùng thư viện Locust hoặc script Python đa luồng bắn thử hàng loạt request cùng lúc để test độ chịu tải của cơ chế khóa Database.
