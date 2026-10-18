# HƯỚNG DẪN CẤU HÌNH GỬI EMAIL BẢO MẬT BẰNG GMAIL

Để gửi email trực tiếp từ website của bạn một cách bảo mật mà **không lộ mật khẩu tài khoản chính**, chúng ta sẽ sử dụng tính năng **Mật khẩu ứng dụng (App Password)** của Google. Dưới đây là các bước thiết lập chi tiết:

---

## Bước 1: Kích hoạt Xác minh 2 bước (2-Step Verification)
*Gmail yêu cầu phải bật xác minh 2 bước thì mới cho phép tạo Mật khẩu ứng dụng.*

1. Truy cập vào trang quản lý tài khoản Google của bạn tại: [https://myaccount.google.com/](https://myaccount.google.com/)
2. Chọn mục **Bảo mật (Security)** ở danh sách bên trái.
3. Tìm phần **Cách bạn đăng nhập vào Google (How you sign in to Google)**.
4. Nếu **Xác minh 2 bước (2-Step Verification)** đang ở trạng thái *Tắt*, hãy click vào đó và làm theo hướng dẫn của Google để bật lên (qua số điện thoại hoặc app Authenticator).

---

## Bước 2: Tạo Mật khẩu ứng dụng (App Password)
1. Sau khi bật Xác minh 2 bước, quay lại phần **Bảo mật (Security)**.
2. Click vào **Xác minh 2 bước (2-Step Verification)**.
3. Cuộn xuống cuối trang, bạn sẽ thấy mục **Mật khẩu ứng dụng (App passwords)**. Click vào mục này.
4. Nhập tên ứng dụng của bạn để dễ quản lý, ví dụ: `Website FPT Telecom`.
5. Click nút **Tạo (Create)**.
6. Google sẽ hiển thị một ô chứa **mật khẩu gồm 16 ký tự màu vàng** (ví dụ: `abcd efgh ijkl mnop`). 
7. Hãy **sao chép mật khẩu này** (bỏ các dấu cách khi điền vào cấu hình). *Lưu ý: Mật khẩu này chỉ xuất hiện 1 lần duy nhất.*

---

## Bước 3: Cấu hình vào dự án
1. Tạo một file mới tên là `.env.local` ở thư mục gốc của dự án (nằm cùng cấp với file `package.json`).
2. Sao chép nội dung từ file `.env.example` sang `.env.local`.
3. Điền thông tin tài khoản của bạn vào `.env.local`:

```env
# Cấu hình SMTP của Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=email-gui-di-cua-ban@gmail.com
SMTP_PASS=mat-khau-ung-dung-16-ky-tu-vua-copy
RECEIVER_EMAIL=email-nhan-thong-tin-khach-hang@gmail.com
```

*Lưu ý:*
- Hãy bỏ hết khoảng trắng trong chuỗi 16 ký tự mật khẩu của bạn khi dán vào `SMTP_PASS`.
- File `.env.local` được Next.js tự động bảo mật và nằm trong danh sách `.gitignore`, nên sẽ **không bao giờ bị đẩy lên GitHub** hay lộ ra bên ngoài.

---

## Ưu điểm bảo mật
- **Không lộ mật khẩu chính**: Mật khẩu ứng dụng chỉ cấp quyền gửi mail thông qua giao thức SMTP, không thể dùng để đăng nhập vào hộp thư Gmail hay thay đổi thông tin cá nhân của bạn.
- **Dễ dàng thu hồi**: Bạn có thể xóa bỏ mật khẩu này bất kỳ lúc nào trong trang quản lý tài khoản Google mà không ảnh hưởng đến mật khẩu chính.
