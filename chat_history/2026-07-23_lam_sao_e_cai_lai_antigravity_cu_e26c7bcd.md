# Hội Thoại: làm sao để cài lại antigravity cũ

- **ID Phiên:** `e26c7bcd-74d2-4e58-9a6f-c16d9425dbe0`
- **Thời gian:** 09:37:15 23/7/2026
- **Tổng số lượt trao đổi:** 2

---

### 👤 User:

làm sao để cài lại antigravity cũ

---

### 🤖 Assistant:

Để cài đặt lại phiên bản cũ (hoặc hạ cấp - downgrade) của **Antigravity**, bạn có thể thực hiện theo các cách dưới đây tùy thuộc vào phiên bản bạn đang sử dụng:

### 1. Đối với VS Code Extension (Antigravity IDE)
Nếu bạn đang dùng Antigravity dưới dạng một extension trong VS Code, việc quay về phiên bản cũ rất đơn giản bằng tính năng tích hợp sẵn:
1. Mở VS Code, nhấn tổ hợp phím `Ctrl + Shift + X` để vào mục **Extensions**.
2. Tìm kiếm extension **Antigravity**.
3. Nhấp vào **biểu tượng bánh răng cưa (Manage)** bên cạnh tên extension (hoặc click chuột phải vào nó).
4. Chọn **"Install Another Version..."** (Cài đặt phiên bản khác...).
5. Một danh sách các phiên bản cũ sẽ hiện ra ở phía trên cùng, bạn chỉ cần chọn phiên bản mong muốn.
6. Sau khi cài xong, nhấn **Reload Required** để áp dụng thay đổi.
> [!TIP]
> Để tránh việc VS Code tự động cập nhật extension này lên bản mới nhất ngay sau đó, bạn có thể click vào bánh răng cưa và bỏ tích chọn **Auto Update** cho riêng extension này.

---

### 2. Đối với Antigravity CLI (`agy`) hoặc Desktop App (Antigravity 2.0)
Trình cài đặt chính thức của Google cho CLI và ứng dụng Desktop mặc định luôn tải về phiên bản mới nhất. Nếu bạn muốn cài đặt lại sạch sẽ (clean reinstall) hoặc hạ cấp:

#### Bước 1: Gỡ bỏ hoàn toàn phiên bản hiện tại (Clean Uninstall)
* **Trên Windows:**
  1. Gỡ cài đặt **Antigravity 2.0** thông qua *Settings > Apps > Installed Apps*.
  2. Xóa file thực thi của CLI: `%LOCALAPPDATA%\agy\bin\agy.exe` (nếu có).
  3. Xóa các thư mục lưu cấu hình và cache bị lỗi bằng cách nhấn `Win + R`, dán các đường dẫn sau và xóa thư mục bên trong:
     * `%APPDATA%\Antigravity`
     * `%LOCALAPPDATA%\Antigravity`
     * `C:\Users\hp\.gemini\antigravity` (thư mục app data hiện tại của bạn)

* **Trên macOS / Linux:**
  1. Xóa file CLI: `rm ~/.local/bin/agy`
  2. Xóa cấu hình: `rm -rf ~/.gemini/antigravity-cli/`

#### Bước 2: Cài đặt lại
* **Nếu bạn có bộ cài đặt cũ (`.exe` hoặc `.msi`):** Chạy trực tiếp file cài đặt cũ đó sau khi đã xóa sạch thư mục cache ở Bước 1.
* **Nếu muốn cài lại bản mới nhất một cách sạch sẽ:** Chạy lệnh cài đặt tương ứng:
  * **Windows (PowerShell):**
    ```powershell
    irm https://antigravity.google/cli/install.ps1 | iex
    ```
  * **macOS / Linux:**
    ```bash
    curl -fsSL https://antigravity.google/cli/install.sh | bash
    ```

---

