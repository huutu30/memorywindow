# 05. Kinh Nghiệm Quản Trị CMS Bài Viết SEO (Supabase Cloud)

## 1. Thiết Kế Cho Người Dùng Không Biết Code
- Giao diện Admin trực quan, soạn thảo nội dung phong phú giống Microsoft Word (hỗ trợ copy-paste trực tiếp từ file `.docx`).
- Tự động tạo Slug chuẩn SEO không dấu từ tiêu đề bài viết tiếng Việt.
- Tự động upload hình ảnh lên Supabase Storage bucket và chèn URL CDN công khai vào bài viết.

## 2. Bảo Mật Đăng Nhập
- Sử dụng mật khẩu quản trị (`ADMIN_PASSWORD`) cấu hình qua biến môi trường.
- Xác thực qua API Route và cấp cookie HTTP-Only an toàn, bảo vệ toàn bộ các route `/admin/*`.
