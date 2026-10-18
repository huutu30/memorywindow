# 07. Hệ Thống Thu Thập Dữ Liệu Khách Hàng Tiềm Năng (Thư Mục `farm`)

## 1. Mục Đích & Phạm Vi
Thư mục `farm` đảm nhận việc quét và thu thập danh bạ/số điện thoại từ các nguồn tin đăng rao vặt, bất động sản, phòng trọ, nhóm kinh doanh để tạo danh sách khách hàng hòa mạng Internet/Truyền hình FPT.

## 2. Các Script Crawler Cốt Lõi
- **`crawl_binhchanh.js` / `crawl_binhtan.js`**: Thu thập số điện thoại theo địa bàn cụ thể (Bình Chánh, Bình Tân, Hóc Môn, Nhà Bè).
- **`crawl_tieu_thuong.js`**: Quét thông tin tiểu thương và hộ kinh doanh.
- **`supercrawl.js`**: Công cụ quét tốc độ cao hỗ trợ nhiều domain bất động sản cùng lúc.
- **`export_data.js` / `export_tieu_thuong.js`**: Phân loại, khử trùng lặp và xuất dữ liệu sang thư mục `export_telesale` phục vụ tư vấn trực tiếp.

## 3. Quản Lý Trạng Thái (State Management)
- Hệ thống duy trì các file `state_<domain>.json` để lưu vết trang đang quét dở dang. Khi chạy lại, crawler tự động tiếp tục từ trang cuối cùng mà không bị lặp lại dữ liệu cũ.
- Khi cần reset để quét lại từ đầu, sử dụng `clean_states.js`.
