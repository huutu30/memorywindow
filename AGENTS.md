<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# AGENTS.md - Quy Chuẩn Phát Triển & Bộ Nhớ Dự Án FPT Telecom Website

> **Tài liệu tổng hợp toàn bộ "bộ nhớ", kinh nghiệm, quy ước lập trình, ràng buộc chính sách Google Ads và sở thích làm việc của User trên máy tính này.**  
> Mọi AI Agent khi làm việc trên dự án này (hoặc các dự án liên quan) **BẮT BUỘC** phải đọc kỹ và tuân thủ tuyệt đối các nguyên tắc dưới đây.

---

## 1. Tổng Quan Dự Án & Mục Tiêu Cốt Lõi

* **Tên dự án**: FPT Telecom Landing Page (`fptwebsite` / `next_fpt`).
* **Mục tiêu**: Trang đích giới thiệu và tiếp nhận **ĐĂNG KÝ HÒA MẠNG MỚI** các dịch vụ của FPT Telecom:
  - Internet WiFi cá nhân / gia đình (WiFi 6, WiFi 7).
  - Combo Internet + Truyền hình FPT Play (bản quyền Ngoại Hạng Anh).
  - FPT Camera an ninh đám mây (Cloud).
* **Định hướng chuyển đổi**:
  - Tối ưu hóa chuyển đổi khách hàng tiềm năng (Leads) qua form đăng ký nhanh và số điện thoại liên hệ trực tiếp.
  - Phân vùng giá cước tự động theo 63 tỉnh/thành (SSG động và Client hydration).
  - Đảm bảo trải nghiệm Mobile First siêu mượt, tốc độ tải trang cực nhanh (PageSpeed Mobile > 80-90+).

---

## 2. Sở Thích & Phong Cách Làm Việc Của User (User Preferences)

1. **Giao tiếp & Hành động**:
   - Giao tiếp ngắn gọn, trực diện, đi thẳng vào vấn đề bằng tiếng Việt tự nhiên.
   - Khi được hỏi giải thích thắc mắc: **Chỉ giải thích nguyên lý/bản chất, không tự ý chỉnh sửa code hay thao tác khi chưa có yêu cầu**.
   - Đối với các tính năng mới hoặc chỉnh sửa cấu trúc lớn: **Luôn lập Kế hoạch (Implementation Plan) trước**, chờ User duyệt rồi mới bắt tay vào code.
   - Sau khi hoàn thành xong yêu cầu: **Chủ động kiểm tra, chạy `git commit` chuẩn và `git push` lên GitHub**.

2. **Khắt khe về Chất Lượng Hình Ảnh & Hiển Thị**:
   - **Tuyệt đối KHÔNG đánh đổi độ sắc nét của hình ảnh để lấy điểm PageSpeed**. Không được nén mờ banner hay giảm chất lượng ảnh hiển thị (User đặc biệt quan tâm đến độ nét Full HD / Crystal Sharp của banner Ngoại Hạng Anh, gói VVIP).
   - Tối ưu ảnh bằng cách: Sử dụng định dạng **WebP**, tạo phiên bản banner riêng cho Desktop (1920px/1200px) và Mobile (1080px/800px) bằng Sharp, tải từ local, không hotlink ra bên ngoài.

3. **Trải Nghiệm Mobile First & Tương Tác**:
   - Đa số khách hàng truy cập bằng điện thoại. Cần chú ý:
     - Tắt các hiệu ứng hover gây nảy/giật layout khi chạm lướt trên màn hình cảm ứng.
     - Section bên dưới màn hình đầu tiên (below-the-fold) phải lazy load mượt mà với `rootMargin` hợp lý (~80px).
     - Không để layout bị giật (CLS - Cumulative Layout Shift), luôn định rõ kích thước hoặc tỷ lệ khung hình.

4. **Cẩn Trọng Từng Chi Tiết Chữ Viết (Copywriting)**:
   - Viết đúng chính tả, đúng hoa/thường (ví dụ: chữ `T` trong FPT, viết hoa tên riêng).
   - Tránh câu từ sáo rỗng hoặc chung chung (như "Đăng Ký Mạng FPT Chính Hãng", "Đường truyền cho doanh nghiệp" khi đang nhắm vào khách cá nhân).

---

## 3. Quy Tắc Sống Còn: Tuân Thủ Chính Sách Google Ads (Third-Party Tech Support Policy)

Website và các chiến dịch quảng cáo đã từng nhận cảnh báo nghiêm khắc từ đội ngũ kiểm duyệt Google Ads về chính sách: **"Dịch vụ hỗ trợ kỹ thuật của bên thứ ba cho người tiêu dùng"**.  
*Yêu cầu từ Google Ads:* **Xóa hoàn toàn mọi thông tin tham chiếu đến dịch vụ lắp ráp/sửa chữa, tư vấn kỹ thuật, thiết lập kết nối hoặc khắc phục sự cố khỏi trang đích và mẫu quảng cáo.**

### 3.1. Danh Sách Từ Khóa CẤM TUYỆT ĐỐI (Forbidden Terms)

| Nhóm từ khóa | Từ ngữ TUYỆT ĐỐI CẤM | Lý do cấm |
| :--- | :--- | :--- |
| **Sửa chữa / Báo hỏng** | `sửa mạng`, `sửa wifi`, `bảo trì`, `báo hỏng`, `báo hư`, `sự cố`, `khắc phục sự cố`, `bị mất mạng`, `mất kết nối` | Google quét nhận diện là dịch vụ sửa chữa bên thứ ba |
| **Thao tác kỹ thuật** | `lắp đặt`, `lắp ráp`, `kéo cáp`, `thi công cáp`, `bấm đầu mạng`, `bấm dây mạng`, `cấu hình thiết bị` | Google xem là dịch vụ kỹ thuật tại gia của bên thứ 3 |
| **Tổng đài & Số nhạy cảm** | `tổng đài`, `tổng đài FPT`, `hotline FPT`, `1900`, `19006600`, `tổng đài viên`, `24/7`, `phục vụ 24/7` | Dễ bị đánh đồng với tổng đài mạo danh / sửa chữa |
| **Từ hỗ trợ nhạy cảm** | `hỗ trợ kỹ thuật`, `hỗ trợ sửa chữa`, `tư vấn kỹ thuật` | Vi phạm trực diện điều khoản chính sách Google |
| **Hạ tầng & Ghép giá sai** | `cáp quang` (ở tiêu đề/mô tả đầu trang), viết ghép "Wifi giá rẻ", "Hòa mạng 299k" | Vi phạm nguyên tắc mẫu quảng cáo và chính sách mạng |

### 3.2. Bảng Chuẩn Hóa Từ Ngữ Thay Thế (Approved Terminology Mapping)

| Cụm từ cũ / Nhạy cảm | Cụm từ CHUẨN THAY THẾ | Ngữ cảnh sử dụng |
| :--- | :--- | :--- |
| `lắp đặt` / `lắp mạng` / `lắp wifi` | **`đăng ký`**, **`hòa mạng`**, **`triển khai dịch vụ`**, **`bàn giao thiết bị`**, **`trang bị`** | Tiêu đề, nút bấm, mô tả gói cước |
| `nhân viên kỹ thuật` | **`đội ngũ triển khai dịch vụ`**, **`đội ngũ kỹ thuật lắp đặt thiết bị ban đầu`** | Quy trình tiếp nhận & hòa mạng |
| `hỗ trợ` / `hỗ trợ khách hàng` | **`chăm sóc`**, **`đồng hành`**, **`phục vụ`**, **`đáp ứng`**, **`hướng dẫn`** | Khối liên hệ, tư vấn gói cước |
| `không mất kết nối` | **`đảm bảo đường truyền luôn thông suốt và mượt mà`** | Gói game thủ, gói gia đình |
| `khi mất mạng` / `rớt mạng` | **`khi thiết bị ngoại tuyến`**, **`khi đường truyền tạm ngưng`** | Câu hỏi thường gặp (FAQs) |
| `cáp quang` | **`đường truyền tốc độ cao`**, **`băng thông rộng`** | Tiêu đề trang, thẻ meta |
| `tổng đài` / `hotline FPT` | **`Hotline đăng ký thuê bao`**, **`Số điện thoại liên hệ`**, **`Đường dây tư vấn`** | Khối liên hệ, nút gọi nhanh |
| URL `/ho-tro` | **Đổi thành `/lien-he`** | Route đường dẫn trang liên hệ |

### 3.3. Tuyên Bố Miễn Trừ Trách Nhiệm (Mandatory Footer Disclaimer)

Tại chân trang ([Footer.jsx](file:///c:/Users/hp/Desktop/fptwebsite/components/layout/Footer.jsx)) **BẮT BUỘC** phải giữ vững thông tin minh bạch:
> *"Chúng tôi là kênh thông tin và hỗ trợ đăng ký hòa mạng mới các dịch vụ viễn thông FPT. Chúng tôi không phải là tổng đài chăm sóc khách hàng, hỗ trợ kỹ thuật hay báo hỏng. Quý khách có nhu cầu báo hỏng/sửa chữa vui lòng liên hệ tổng đài chính thức qua ứng dụng Hi FPT."*

### 3.4. Quản Lý Tin Tức & Crawling Bài Viết

- **Ẩn các bài hướng dẫn kỹ thuật**: Toàn bộ bài viết tin tức hướng dẫn đổi mật khẩu wifi, cấu hình modem, sửa lỗi mạng trong [newsData.js](file:///c:/Users/hp/Desktop/fptwebsite/data/newsData.js) phải gắn cờ `hidden: true` (lọc tự động `export const NEWS_DATA = ALL_NEWS.filter(p => !p.hidden)`).
- **Quy tắc crawl bài mới**:
  - Dùng script `update_new/run_crawl.mjs` hoặc script chuyên dụng.
  - Phải chạy qua bộ lọc tự động khử từ nhạy cảm (`lắp đặt` -> `đăng ký`, khử số 1900, đổi các từ cấm).
  - Download toàn bộ ảnh đại diện và ảnh nội dung về thư mục `public/images/news/`, chuyển thành định dạng WebP. **Tuyệt đối không lưu URL trỏ trực tiếp đến `fpt.vn`**.

---

## 4. Kiến Trúc Kỹ Thuật (Tech Stack & Architecture)

```text
├── app/                          # Next.js 16 App Router
│   ├── api/send-email/           # API gửi thông tin đăng ký dịch vụ (Nodemailer SMTP)
│   ├── lap-internet-wifi/[city]/ # SSG động cho 63 tỉnh/thành tối ưu SEO địa phương
│   ├── layout.tsx                # Root Layout, tích hợp Context Providers
│   ├── page.tsx                  # Trang chủ (Server Component)
│   ├── HomeClient.jsx            # Giao diện chính phía Client (Tabs, Banners, Slider)
│   └── globals.css               # Tailwind CSS v4 & custom animations
├── components/
│   ├── common/                   # ProductCardSlider, Modals, FloatingContact, LazySection
│   ├── home/                     # HeroBanner, VvipSportsCombo, DiscoverySection, NewsSection
│   └── layout/                   # Navbar, Footer (kèm Disclaimer)
├── context/
│   ├── RegionContext.jsx         # Xác định tỉnh thành hiện tại từ URL hoặc LocalStorage
│   ├── RegisterContext.jsx       # Modal đăng ký nhanh
│   └── ProductDetailContext.jsx  # Modal thông tin chi tiết gói cước
├── data/
│   ├── products/                 # Chi tiết gói internet, camera, truyenHinh, wifi7
│   ├── cityData.js               # Danh sách slug & tên 63 tỉnh thành
│   ├── provincePrices.js         # Bảng giá chi tiết từng gói cước theo từng tỉnh
│   ├── priceHelper.js            # Engine tính toán giá (tỉnh -> khu vực HCM/Tỉnh -> fallback)
│   ├── productData.js            # Aggregator gom toàn bộ danh mục sản phẩm
│   └── newsData.js               # Cơ sở dữ liệu bài viết tin tức (có lọc hidden)
├── update_new/                   # Scripts crawler & Sharp nén banner
├── indexnow-ping.js              # Script ping URL tự động lên IndexNow (Google, Bing)
└── public/images/                # Kho lưu trữ ảnh WebP nội bộ
```

### 4.1. Quy Ước Next.js 16 (App Router Breaking Changes)
- **Async Route Params**: Trong Next.js 16, các tham số `params` và `searchParams` trong Page/Layout là Promise. Bắt buộc `await params`:
  ```javascript
  export default async function Page({ params }) {
    const { city } = await params;
    // ...
  }
  ```
- **Image Optimization**: Sử dụng thẻ `Image` của Next.js với thuộc tính `priority` cho các banner above-the-fold, và `loading="lazy"` cho các ảnh phía dưới.

### 4.2. Logic Tính Giá Theo Địa Phương (Pricing Engine)
1. Khách truy cập `/lap-internet-wifi/[city]` -> `RegionContext` nhận diện `city` từ slug.
2. Khách truy cập trang chung -> khôi phục từ `localStorage` (mặc định: `toan-quoc`).
3. Phân loại khu vực (`region`):
   - `'hcm'`: Áp dụng cho Hà Nội và TP. Hồ Chí Minh nội thành.
   - `'tinh'`: Áp dụng cho ngoại thành và toàn bộ các tỉnh thành khác.
4. Hàm `getProductPrice(product, activeCity, region)` trong [priceHelper.js](file:///c:/Users/hp/Desktop/fptwebsite/data/priceHelper.js):
   - Nếu tìm thấy giá khớp chính xác với `activeCity` và `product.id` trong `provincePrices.js` -> dùng giá đó.
   - Nếu không -> fallback về giá vùng `product.price[region]`.

### 4.3. Cấu Hình Email Đăng Ký (Nodemailer SMTP)
- Hệ thống gửi email tự động khi khách hàng điền form đăng ký tư vấn.
- Sử dụng **Gmail App Password (16 ký tự)**, không dùng mật khẩu chính:
  ```env
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=465
  SMTP_USER=email-gui@gmail.com
  SMTP_PASS=xxxx-xxxx-xxxx-xxxx
  RECEIVER_EMAIL=email-nhan-thong-tin@gmail.com
  ```
- File `.env.local` luôn nằm trong `.gitignore`, tuyệt đối không commit lên GitHub.

---

## 5. Quy Chuẩn Google Ads & Tối Ưu Chiến Dịch

* **Mô hình đấu thầu**: Ưu tiên **CPA mục tiêu (Target CPA ~150k)**. Tránh thả rông CPA hoặc tối đa hóa lượt nhấp (dễ bị cạn ngân sách nhanh mà không ra lead thực tế).
* **Thiết bị**: Thường ưu tiên Mobile, có thể giảm thầu Desktop 100% khi tập trung ngân sách.
* **Quy tắc mẫu quảng cáo (Responsive Search Ads)**:
  - **15 Tiêu đề (Headlines)**: Độ dài < 30 ký tự, **tuyệt đối không chứa giá tiền cụ thể** trong 15 tiêu đề, không chứa từ cấm.
  - **4 Mô tả (Descriptions)**: Độ dài < 90 ký tự, đầy đủ thông tin ưu đãi, thủ tục CCCD nhanh gọn, quà tặng modem WiFi 6 / Camera.
  - Tham khảo tài liệu chuẩn tại [Chien_Dich_Google_Ads_FPT_Moi.txt](file:///c:/Users/hp/Desktop/fptwebsite/Chien_Dich_Google_Ads_FPT_Moi.txt).
* **Từ khóa phủ định (Negative Keywords)**:
  - Duy trì danh sách phủ định nghiêm ngặt tại [tu_khoa_phu_dinh_unique.txt](file:///c:/Users/hp/Desktop/fptwebsite/tu_khoa_phu_dinh_unique.txt) với hơn 340+ cụm từ về: bảo trì, sửa mạng, báo hỏng, tổng đài, bấm cáp, hack wifi, v.v. để không bị hao ngân sách vào các cuộc gọi sai mục đích.

---

## 6. Bài Học Kinh Nghiệm Từ Các Dự Án Khác Trên Máy

1. **Dự án `ongnhua` / `ongnhuagiasi.id.vn`**:
   - Hệ thống CMS quản trị bài viết chuẩn SEO kết nối Supabase Cloud.
   - Quản trị viên không biết code: Cần giao diện trực quan, tự động tạo slug chuẩn SEO không dấu, upload ảnh tự động lên CDN Storage.
   - Bảo mật đăng nhập admin bằng HTTP-Only cookie, cấu hình `ADMIN_PASSWORD` qua biến môi trường.

2. **Dự án tự động hóa `cache` & `crawl`**:
   - Tự động hóa qua Chrome Remote Debugging (cổng 9222 và 9223).
   - Khi chạy script Python trên môi trường PowerShell Windows, bắt buộc cấu hình `sys.stdout.reconfigure(encoding='utf-8')` để tránh lỗi crash do tiếng Việt có dấu.
   - Cơ chế an toàn: Luôn có cờ `DRY_RUN`, cơ chế hẹn giờ tắt máy (`shutdown /s /t 600`) kèm thông báo rõ ràng cho phép hủy lệnh (`shutdown /a`).

---

## 7. Quy Trình Vận Hành & Git Workflow

1. **Kiểm tra trước khi hoàn thành**:
   - Chạy `npm run build` để kiểm tra compile và type errors nếu có thay đổi code.
   - Đảm bảo không tạo các file ảnh PNG gốc nặng dung lượng trong repo.
   - Xóa bỏ các script scratch tạm thời trước khi bàn giao.
2. **Git Commit & Push**:
   - Sử dụng chuẩn Conventional Commits:
     - `feat:` Thêm tính năng mới hoặc component mới.
     - `fix:` Sửa lỗi hiển thị, logic hoặc lỗi tuân thủ.
     - `perf:` Tối ưu hóa hiệu năng, PageSpeed, nén ảnh.
     - `docs:` Cập nhật tài liệu, hướng dẫn, AGENTS.md.
     - `chore:` Dọn dẹp cấu hình, scripts vận hành.
   - Thực hiện lệnh:
     ```bash
     git add <cac_file_thay_doi>
     git commit -m "docs: cap nhat AGENTS.md toan dien quy chuan bo nho va chinh sach"
     git push origin main
     ```
