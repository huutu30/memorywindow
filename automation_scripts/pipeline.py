import os
import sys
import time
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def prevent_windows_sleep():
    """Giữ Windows luôn thức (ngăn chế độ Sleep/Standby) trong suốt quá trình treo máy xuyên đêm"""
    try:
        import ctypes
        # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000040)
        print("⚡ Đã kích hoạt cơ chế chống Sleep Windows: Giữ máy tính hoạt động ổn định 100% đến khi tắt máy.")
    except Exception:
        pass

def main():
    prevent_windows_sleep()

    # Đọc cấu hình mục tiêu và hẹn giờ tắt máy từ tham số dòng lệnh
    target_count = 800
    countdown = 600  # 10 phút = 600 giây
    do_shutdown = "--no-shutdown" not in sys.argv

    for idx, arg in enumerate(sys.argv):
        if arg == "--target" and idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            target_count = int(sys.argv[idx + 1])
        elif arg == "--countdown" and idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            countdown = int(sys.argv[idx + 1])

    print("=" * 70)
    print(f"      QUY TRÌNH TREO MÁY TỰ ĐỘNG TOÀN DIỆN (PIPELINE {target_count} HỘI THOẠI)")
    print("=" * 70)
    print(f"  [1] Giai đoạn 1: type.py (Cổng CDP: 9223) -> Tạo đủ {target_count} hội thoại khách hàng")
    print(f"  [2] Giai đoạn 2: run.py  (Cổng CDP: 9222) -> Tự động điền địa chỉ {target_count} hội thoại")
    print(f"  [3] Giai đoạn 3: Tự động tắt máy sau {countdown // 60} phút ({'BẬT' if do_shutdown else 'TẮT'})")
    print("=" * 70)

    # Tự động sao lưu và làm mới lịch sử để đảm bảo đếm đủ hội thoại mới của đợt này
    is_resume = "--resume" in sys.argv or "--no-reset" in sys.argv
    args_run = ["--auto", "--target", str(target_count)]

    if not is_resume:
        # Sao lưu file lịch sử cũ nếu có
        history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_history.json")
        if os.path.exists(history_file):
            backup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_history_backup.json")
            try:
                import shutil
                shutil.copyfile(history_file, backup_file)
                print("💾 Đã tự động sao lưu lịch sử cũ vào: processed_history_backup.json")
            except Exception:
                pass
        args_run.append("--reset")
        print(f"💡 Tự động bật chế độ làm mới (--reset): Đếm chuẩn xác {target_count} hội thoại cho đợt chạy này.")
        print("   (Ghi chú: Nếu cần chạy nối tiếp phiên bị ngắt, hãy dùng lệnh: python pipeline.py --resume)")
    else:
        print("💡 Đang chạy chế độ tiếp tục (--resume): Giữ nguyên lịch sử để chạy nối tiếp.")

    if do_shutdown:
        args_run.extend(["--shutdown", "--countdown", str(countdown)])

    print("\n⏳ Hệ thống sẽ BẮT ĐẦU tự động sau 3 giây... (Nhấn Ctrl + C nếu muốn dừng)")
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nĐã hủy.")
        return

    # --- BƯỚC 1: CHẠY TYPE.PY (CỔNG 9223) ---
    print("\n" + "#" * 70)
    print(f">>> BƯỚC 1/2: KHỞI CHẠY type.py TRÊN CỔNG 9223 (MỤC TIÊU {target_count} HỘI THOẠI) <<<")
    print("#" * 70 + "\n")
    
    t0_type = time.time()
    res1 = subprocess.run([sys.executable, "type.py", "--auto", "--target", str(target_count)])
    
    if res1.returncode != 0:
        print(f"\n⚠️ type.py kết thúc với mã lỗi {res1.returncode}.")
        print("Vui lòng kiểm tra Chrome cổng 9223 xem có đang mở trang web fptlapmang không.")
        choice = input("Bạn có muốn tiếp tục chạy run.py không? (y/n): ").strip().lower()
        if choice != 'y':
            return
    else:
        mins = int((time.time() - t0_type) / 60)
        print(f"\n✅ [HOÀN TẤT BƯỚC 1/2] type.py đã tạo đủ {target_count} hội thoại thành công trong {mins} phút!")

    # --- BƯỚC ĐỒNG BỘ ---
    print("\n⏳ Đang nghỉ 8 giây để Portal SOP (cổng 9222) đồng bộ toàn bộ tin nhắn mới...")
    time.sleep(8)

    # --- BƯỚC 2: CHẠY RUN.PY (CỔNG 9222) ---
    print("\n" + "#" * 70)
    print(f">>> BƯỚC 2/2: KHỞI CHẠY run.py TRÊN CỔNG 9222 (ĐIỀN ĐỊA CHỈ HỘI THOẠI) <<<")
    print("#" * 70 + "\n")

    cmd_run = [sys.executable, "run.py"] + args_run
    res2 = subprocess.run(cmd_run)

    print("\n🎉 Hoàn thành toàn bộ quy trình.")

    # --- BƯỚC 3: HẸN GIỜ TẮT MÁY (10 PHÚT) ---
    if do_shutdown and res2.returncode == 0:
        print("\n" + "=" * 70)
        print(f"🛑 [CHẾ ĐỘ HẸN GIỜ TẮT MÁY ĐƯỢC KÍCH HOẠT]")
        print(f"⏰ Toàn bộ {target_count} hội thoại đã hoàn thành! Máy tính sẽ tắt nguồn sau {countdown // 60} phút ({countdown} giây)...")
        print("👉 Nếu bạn đang ngồi trước máy và muốn hủy tắt, hãy mở CMD/PowerShell gõ: shutdown /a")
        print("=" * 70)
        time.sleep(2)
        os.system(f"shutdown /s /t {countdown}")

if __name__ == "__main__":
    main()
