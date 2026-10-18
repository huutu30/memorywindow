# 🧠 MemoryWindow - Trung Tâm Quản Trị Bộ Nhớ & Quy Chuẩn Lập Trình AI

> **Dự án lưu trữ tập trung toàn bộ "bộ nhớ", kinh nghiệm thực chiến, quy ước lập trình, ràng buộc chính sách Google Ads và sở thích cá nhân của User trên máy tính.**

---

## 🎯 Mục Đích & Ý Nghĩa Dự Án

Khi làm việc với các trợ lý AI (như Antigravity, Gemini, Claude Code, Cursor, Copilot), các AI thường bị "mất trí nhớ" hoặc quên đi các kinh nghiệm quý báu đã từng giải quyết trong quá khứ. 

**MemoryWindow** được tạo ra nhằm mục đích:
1. **Lưu trữ vĩnh viễn** toàn bộ phong cách làm việc, sở thích và quy chuẩn khắt khe của bạn.
2. **Ngăn chặn lặp lại sai lầm**: Đặc biệt là các cảnh báo vi phạm chính sách của Google Ads (Dịch vụ hỗ trợ kỹ thuật bên thứ ba) hay lỗi làm mờ banner ảnh khi tối ưu PageSpeed.
3. **Đồng bộ đa nền tảng**: Cung cấp sẵn các file cấu hình chuẩn (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) để có thể áp dụng hoặc sao chép ngay sang bất kỳ dự án mới nào trên máy tính chỉ với 1 lệnh script.

---

## 📁 Cấu Trúc Thư Mục

```text
memorywindow/
├── AGENTS.md                  # Quy chuẩn tổng hợp đa năng cho mọi AI Agent
├── CLAUDE.md                  # Cấu hình chuẩn cho Claude Code / Anthropic
├── GEMINI.md                  # Cấu hình chuẩn cho Gemini AI / Antigravity IDE
├── README.md                  # Tài liệu giới thiệu tổng quan dự án
├── .gitignore                 # Cấu hình bỏ qua file tạm & bảo mật
│
├── knowledge/                 # Cơ sở tri thức chi tiết theo từng chuyên đề
│   ├── 01-so-thich-user.md    # Phong cách giao tiếp, thẩm mỹ hình ảnh & trải nghiệm Mobile
│   ├── 02-chinh-sach-google-ads.md # Bảng từ cấm, từ thay thế, quy tắc mẫu quảng cáo
│   ├── 03-quy-chuan-nextjs-web.md  # Quy ước Next.js 16, React 19, tối ưu WebP Sharp, PageSpeed
│   ├── 04-kinh-nghiem-automation.md # Tự động hóa Chrome CDP (9222/9223), Playwright, Anti-ban
│   └── 05-kinh-nghiem-supabase-cms.md # CMS quản trị chuẩn SEO kết nối Supabase Cloud
│
├── data/                      # Dữ liệu tài nguyên quan trọng
│   ├── tu_khoa_phu_dinh_google_ads.txt # 340+ từ khóa phủ định loại trừ báo hỏng, sửa chữa
│   └── mau_quang_cao_chuan.txt         # Bộ 15 tiêu đề & 4 mô tả chuẩn chính sách Google Ads
│
└── scripts/
    └── sync_to_project.ps1    # Script tự động copy AGENTS.md sang các dự án khác
```

---

## 🚀 Cách Sử Dụng Cho Dự Án Mới

Mỗi khi bạn bắt đầu một dự án mới trên máy tính (ví dụ: `c:\Users\hp\Desktop\du-an-moi`), bạn chỉ cần:
1. Mở PowerShell tại thư mục `memorywindow`:
   ```powershell
   .\scripts\sync_to_project.ps1 -TargetDir "c:\Users\hp\Desktop\du-an-moi"
   ```
2. AI Agent khi mở dự án mới đó sẽ tự động đọc `AGENTS.md` / `CLAUDE.md` và tuân thủ ngay từ đầu mọi sở thích và quy chuẩn của bạn mà không cần phải nhắc lại!
