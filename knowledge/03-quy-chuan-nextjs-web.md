# 03. Quy Chuẩn Kỹ Thuật: Next.js 16, React 19 & Tối Ưu Web

## 1. Lưu Ý Breaking Changes Của Next.js 16
- **Async Route Params**: Trong Next.js 16 App Router, `params` và `searchParams` là Promise. Bắt buộc dùng `await params`.
- **Server Components & Client Components**: Phân tách rõ ràng với chỉ thị `"use client"`. Các trang tĩnh SSG render trên Server để tối ưu SEO, chỉ phần tương tác (Tabs, Modals, Sliders) mới đẩy sang Client.

## 2. Chiến Lược Tối Ưu Hình Ảnh & PageSpeed
- Nén ảnh với **Sharp** sang WebP chất lượng cao (quality 85-90).
- Sử dụng thẻ `Image` của Next.js với `priority` cho banner màn hình đầu (above-the-fold) và `loading="lazy"` cho phần còn lại.
- Dùng `IntersectionObserver` với `rootMargin: "80px"` để trì hoãn nạp các component nặng dưới trang.

## 3. Kiến Trúc Định Giá Đa Vùng (Pricing Engine)
- Hệ thống hỗ trợ định giá riêng cho 63 tỉnh/thành:
  - Route động: `/lap-internet-wifi/[city]`
  - Fallback về 2 vùng miền chính: `hcm` (Hà Nội & TP.HCM nội thành) và `tinh` (ngoại thành và các tỉnh khác).
  - Tra cứu giá chính xác theo mã tỉnh trong bảng dữ liệu trước, nếu không có mới lấy giá vùng chung.

## 4. Bảo Mật Biến Môi Trường (SMTP Email)
- Toàn bộ thông tin nhạy cảm (SMTP Pass, DB Pass, API Key) lưu tại `.env.local`.
- File `.env.local` luôn nằm trong `.gitignore`, không bao giờ commit lên GitHub.
