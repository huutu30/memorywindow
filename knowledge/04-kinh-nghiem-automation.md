# 04. Kinh Nghiệm Thực Chiến: Tự Động Hóa Browser (CDP & Playwright)

## 1. Kết Nối Trình Duyệt Đang Chạy (Chrome Remote Debugging)
- Sử dụng các cổng chuyên dụng để tương tác với profile Chrome thực tế mà không bị chặn bot:
  - Cổng `9222`: Thường dùng cho trang quản trị / Portal CRM / Zalo Web.
  - Cổng `9223`: Dùng cho bot gửi tin nhắn / tạo hội thoại khách hàng mới.

## 2. Biện Pháp An Toàn Chống Khóa Tài Khoản (Anti-Ban)
- **Cơ chế chạy thử (`DRY_RUN = True`)**: Luôn có chế độ chạy mô phỏng, ghi log danh sách đối tượng và nội dung tin nhắn mà không click gửi thật.
- **Tạo nội dung ngẫu nhiên (Spin content)**: Tổ hợp đa tầng (lời chào, hook, offer, CTA, emoji, khoảng cách) để không bao giờ có 2 tin nhắn trùng hash.
- **Bộ nhớ lịch sử (`sent_history.json`)**: Lưu lại các tài khoản đã xử lý để tránh gửi trùng lặp.
- **Human Delay**: Giãn cách an toàn từ 25 - 45 giây giữa các tác vụ, mô phỏng gõ phím từ từ.

## 3. Cơ Chế Tắt Máy An Toàn Trên Windows
- Khi hoàn tất khối lượng công việc (batch), hệ thống kích hoạt hẹn giờ tắt nguồn an toàn:
  ```python
  os.system("shutdown /s /t 600") # 10 phút = 600 giây
  ```
- Luôn in thông báo đếm ngược rõ ràng và hướng dẫn lệnh hủy: `shutdown /a`.

## 4. Xử Lý Tiếng Việt Trên Console PowerShell Windows
- PowerShell Windows thường bị lỗi mã hóa UTF-8 với ký tự có dấu.
- Bắt buộc khai báo ở đầu script Python:
  ```python
  import sys
  if hasattr(sys.stdout, 'reconfigure'):
      sys.stdout.reconfigure(encoding='utf-8')
  ```
