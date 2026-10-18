# 🧠 MemoryWindow - Kho Lưu Trữ Toàn Diện Bộ Nhớ, Mã Nguồn & Quy Chuẩn Hệ Thống

> **Dự án trung tâm lưu trữ toàn bộ mã nguồn công cụ, lịch sử hội thoại, kinh nghiệm lập trình, chính sách quảng cáo và sở thích của User trên toàn bộ máy tính.**

---

## 📁 Cấu Trúc Tổng Thể

```text
memorywindow/
├── AGENTS.md                  # Quy chuẩn gốc cho mọi AI Agent trên máy tính
├── CLAUDE.md                  # Cấu hình chuẩn cho Claude Code (@AGENTS.md)
├── GEMINI.md                  # Cấu hình chuẩn cho Gemini AI / Antigravity IDE
├── README.md                  # Mục lục và hướng dẫn trung tâm
├── .gitignore                 # Cấu hình loại trừ file rác / bảo mật
│
├── chat_history/              # Toàn bộ 29 phiên hội thoại AI đã được trích xuất (.md)
│   ├── README.md              # Bảng tra cứu lịch sử theo ngày tháng và chủ đề
│   └── *.md                   # Từng cuộc hội thoại chi tiết
│
├── knowledge/                 # Cơ sở tri thức chuyên sâu
│   ├── 01-so-thich-user.md    # Giao tiếp trực diện, duyệt Plan trước, giữ độ nét ảnh Crystal Sharp
│   ├── 02-chinh-sach-google-ads.md # Bảng từ cấm, từ thay thế, disclaimer, quy tắc Google Ads
│   ├── 03-quy-chuan-nextjs-web.md  # Next.js 16 breaking changes, Sharp WebP, PageSpeed > 80-90+
│   ├── 04-kinh-nghiem-automation.md # Chrome CDP 9222/9223, anti-ban, hẹn giờ tắt máy, UTF-8
│   ├── 05-kinh-nghiem-supabase-cms.md # CMS quản trị bài viết chuẩn SEO kết nối Supabase Cloud
│   ├── 06-he-thong-automation-cache.md # Toàn bộ kiến trúc tool tự động hóa thư mục cache
│   ├── 07-he-thong-crawler-lead-farm.md # Kiến trúc công cụ cào số điện thoại thư mục farm
│   └── 08-huong-dan-trien-khai-vercel-domain.md # Cấu hình deploy Vercel & khắc phục phân quyền
│
├── automation_scripts/        # Toàn bộ mã nguồn tự động hóa SOP & Zalo (từ thư mục cache)
│   ├── pipeline.py            # Chạy tự động khép kín & hẹn giờ tắt máy 10 phút
│   ├── type.py                # Bot tạo hội thoại khách hàng mới (cổng 9223)
│   ├── run.py                 # Bot điền thông tin địa chỉ khách hàng (cổng 9222)
│   ├── auto_campaign.py       # Tự động hóa copy chiến dịch & cập nhật hợp đồng
│   ├── auto_update_status.py  # Cập nhật trạng thái hội thoại tự động
│   ├── auto_lookup_sop.py     # Tra cứu số điện thoại SOP
│   ├── fpl.py                 # Tự động hóa giả lập LDPlayer qua ADB
│   ├── zalo_sender.py         # Bot gửi tin nhắn Zalo Web theo danh bạ
│   ├── tach_sdt.py            # Tiện ích lọc tách số điện thoại
│   └── chay_tool.bat / .ps1   # Các kịch bản chạy nhanh
│
├── crawler_scripts/           # Toàn bộ mã nguồn cào dữ liệu khách hàng (từ thư mục farm)
│   ├── crawl_binhchanh.js     # Cào số điện thoại khu vực Bình Chánh / Hóc Môn / Nhà Bè
│   ├── crawl_binhtan.js       # Cào số điện thoại khu vực Bình Tân
│   ├── crawl_tieu_thuong.js   # Cào số điện thoại tiểu thương hộ kinh doanh
│   ├── supercrawl.js          # Bộ quét đa luồng tốc độ cao
│   └── export_data.js         # Khử trùng lặp và xuất dữ liệu telesale
│
├── google_ads_resources/      # Toàn bộ tài nguyên & báo cáo chiến dịch Google Ads
│   ├── Chien_Dich_Google_Ads_FPT_Moi.txt # 15 tiêu đề, 4 mô tả, danh sách từ khóa chuẩn
│   ├── tu_khoa_phu_dinh_unique.txt       # 340+ từ khóa phủ định loại bỏ báo hỏng, sửa chữa
│   └── Bao_cao_chi_tiet_tu_khoa_phu_dinh.xml # Dữ liệu phân tích từ khóa phủ định
│
├── project_guides/            # Hướng dẫn kỹ thuật & script hỗ trợ
│   ├── HUONG_DAN_EMAIL.md     # Cấu hình SMTP Gmail App Password bảo mật
│   ├── chinhsachbaomat.txt    # Nội dung chính sách bảo mật cho website
│   └── indexnow-ping.js       # Tự động gửi URL ping lên IndexNow API
│
└── scripts/
    └── sync_to_project.ps1    # Script đồng bộ AGENTS.md sang bất kỳ dự án nào khác
```

---

## 🚀 Cách Đẩy Lên GitHub 1 Lần Duy Nhất

1. Tạo một repository mới trên GitHub đặt tên là **`memorywindow`** (khuyến nghị chọn **Public**).
2. Chạy lệnh tại thư mục `memorywindow`:
   ```bash
   git remote add origin https://github.com/<tai-khoan>/memorywindow.git
   git push -u origin main
   ```
Toàn bộ mã nguồn tự động hóa, cào dữ liệu, bộ tài liệu quảng cáo và 29 phiên hội thoại sẽ được lưu trữ an toàn trên đám mây!
