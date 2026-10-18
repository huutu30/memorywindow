# 08. Hướng Dẫn Triển Khai (Deploy) Vercel & Tên Miền Riêng

## 1. Lưu Ý Về Quyền Hạn Deploy Trên Vercel Hobby
- **Nguyên nhân lỗi**: Khi một tài khoản GitHub đẩy commit lên repo Private thuộc quyền quản lý của một tài khoản Vercel khác, Vercel Hobby sẽ từ chối tự động build và yêu cầu nâng cấp lên Pro ($20/tháng).
- **Giải pháp miễn phí 100%**:
  1. **Đổi Repo sang Public**: Vào GitHub Repo `Settings` ➔ `Danger Zone` ➔ `Change visibility` ➔ `Change to public`. Vercel sẽ tự động build mọi commit mà không yêu cầu tài khoản Pro.
  2. **Hoặc Deploy trực tiếp bằng Vercel CLI**: Chạy `npx vercel --prod` ngay trong thư mục máy tính, bỏ qua bước kiểm tra quyền hạn của GitHub.

## 2. Cấu Hình Tên Miền Riêng (Custom Domain)
- **A Record**:
  - Type: `A` | Name: `@` | Value: `76.76.21.21`
- **CNAME Record**:
  - Type: `CNAME` | Name: `www` | Value: `cname.vercel-dns.com`
