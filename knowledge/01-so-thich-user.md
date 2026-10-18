# 01. Sở Thích & Phong Cách Làm Việc Của User (User Preferences)

## 1. Phong Cách Giao Tiếp & Ra Quyết Định
- **Trực diện, ngắn gọn**: Đi thẳng vào giải pháp và kết quả, không dài dòng giải thích những thứ hiển nhiên.
- **Giải thích trước, làm sau**: Khi user đặt câu hỏi thắc mắc, **chỉ giải thích nguyên lý/bản chất vấn đề, tuyệt đối không tự ý chỉnh sửa code hay thao tác khi chưa có lệnh**.
- **Kế hoạch trước khi thực thi**: Với tính năng mới, tái cấu trúc hoặc tác vụ phức tạp, luôn tạo Kế hoạch (Plan) và chờ user phê duyệt rồi mới bắt tay vào code.
- **Tự giác Git**: Sau khi hoàn thành xong yêu cầu, chủ động kiểm tra trạng thái, commit rõ ràng theo chuẩn Conventional Commits và push lên GitHub.

## 2. Tiêu Chuẩn Thẩm Mỹ & Độ Sắc Nét Của Hình Ảnh
- **KHÔNG BAO GIỜ đánh đổi độ nét lấy điểm PageSpeed**: User rất nhạy cảm với hình ảnh mờ/nén quá tay. Mọi banner chương trình (như Ngoại Hạng Anh, gói VVIP) bắt buộc phải đạt độ nét Full HD / Crystal Sharp.
- **Phương pháp tối ưu**:
  - Không hotlink ảnh từ bên ngoài (như fpt.vn).
  - Tải ảnh về lưu trữ nội bộ (local).
  - Dùng Sharp nén sang định dạng WebP với cấu hình riêng cho Desktop (1920px/1200px) và Mobile (1080px/800px).
  - Tối ưu kích thước DOM và tỷ lệ khung hình cố định để triệt tiêu CLS (Cumulative Layout Shift).

## 3. Tối Ưu Trải Nghiệm Mobile First
- **Cảm ứng di động**: Tắt toàn bộ hiệu ứng hover gây rung/nảy layout khi ngón tay vô tình chạm lướt trên màn hình cảm ứng điện thoại.
- **Lazy loading thông minh**: Sử dụng LazySection với `rootMargin` vừa phải (~80px) để không tải trước nội dung bên dưới khi chưa cuộn tới, giữ PageSpeed Mobile > 80-90+.

## 4. Ngữ Nghĩa & Copywriting
- Viết hoa đúng chính tả thương hiệu (ví dụ: chữ `T` trong FPT).
- Tránh các từ ngữ sáo rỗng hoặc thông điệp sai tệp khách hàng mục tiêu (ví dụ: không dùng "Đường truyền doanh nghiệp" cho trang nhắm vào hộ gia đình/cá nhân).
