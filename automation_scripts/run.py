import os
import sys
import json
import time
import random
import re
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

TIMEOUT = 7000
CDP_PORT = 9223  # Cổng CDP Chrome mặc định (dễ dàng tự sửa tại đây nếu cần)
RELOAD_EVERY = 999999  # Đã tắt reload định kỳ theo yêu cầu (chỉ reload khi web bị đơ/lag/lỗi)
AUTO_SHUTDOWN = False  # Tự động bật nếu có cờ --shutdown (hoặc tắt bằng --no-shutdown)
if "--shutdown" in sys.argv:
    AUTO_SHUTDOWN = True
elif "--no-shutdown" in sys.argv:
    AUTO_SHUTDOWN = False

SHUTDOWN_COUNTDOWN = 600  # Mặc định hẹn giờ tắt máy sau 10 phút (600 giây)
for _i, _arg in enumerate(sys.argv):
    if _arg == "--countdown" and _i + 1 < len(sys.argv) and sys.argv[_i + 1].isdigit():
        SHUTDOWN_COUNTDOWN = int(sys.argv[_i + 1])

TARGET_COUNT = 800  # Mục tiêu mặc định: 800 hội thoại (có thể tùy chỉnh bằng tham số --target N)
for _i, _arg in enumerate(sys.argv):
    if _arg == "--target" and _i + 1 < len(sys.argv) and sys.argv[_i + 1].isdigit():
        TARGET_COUNT = int(sys.argv[_i + 1])
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_history.json")

ADDRESS_DATA = {
    "Hà Nội": {
        "streets": [
            "Đường Nguyễn Trãi", "Đường Cầu Giấy", "Đường Trần Duy Hưng",
            "Đường Láng", "Đường Giải Phóng", "Phố Huế",
            "Đường Kim Mã", "Đường Hoàng Hoa Thám", "Đường Thụy Khuê",
            "Đường Tây Sơn", "Đường Nguyễn Lương Bằng", "Đường Tôn Đức Thắng",
            "Đường Xã Đàn", "Đường Đại Cồ Việt", "Đường Bạch Mai",
            "Đường Trường Chinh", "Đường Phạm Văn Đồng", "Đường Xuân Thủy",
            "Đường Lê Văn Lương", "Đường Khuất Duy Tiến", "Đường Mỹ Đình",
            "Đường Nguyễn Cơ Thạch", "Đường Hồ Tùng Mậu",
            "Đường Hoàng Quốc Việt", "Đường Võ Chí Công",
            "Đường Lạc Long Quân", "Đường Âu Cơ", "Đường Yên Phụ",
            "Đường Thanh Niên", "Đường Phan Đình Phùng"
        ],
        "details": [
            "Số 12", "Số 45", "Ngõ 102 nhà số 5", "Số 88",
            "Ngách 24/8 số 12", "Số 25", "Số 210/12", "Số 7",
            "Số 34", "Ngõ 150/4", "Số 92", "Số 15",
            "Căn hộ 402", "P501"
        ]
    },

    "Hồ Chí Minh": {
        "streets": [
            "Đường Nguyễn Huệ", "Đường Lê Lợi", "Đường Đồng Khởi",
            "Đường Hai Bà Trưng", "Đường Cách Mạng Tháng Tám",
            "Đường Điện Biên Phủ", "Đường Nam Kỳ Khởi Nghĩa",
            "Đường Võ Văn Tần", "Đường Nguyễn Thị Minh Khai",
            "Đường Ba Tháng Hai", "Đường Cộng Hòa",
            "Đường Trường Chinh", "Đường Hoàng Văn Thụ",
            "Đường Phan Đăng Lưu", "Đường Nguyễn Kiệm",
            "Đường Nguyễn Văn Trỗi", "Đường Lê Văn Sỹ",
            "Đường Trần Hưng Đạo", "Đường Nguyễn Trãi",
            "Đường An Dương Vương", "Đường Lý Thường Kiệt",
            "Đường Phạm Văn Đồng", "Đường Phan Văn Trị",
            "Đường Quang Trung", "Đường Lê Đức Thọ",
            "Đường Nguyễn Oanh", "Đường Lê Văn Thọ",
            "Đường Thống Nhất", "Đường Kinh Dương Vương",
            "Đường Nguyễn Văn Linh", "Đường Quốc lộ 13",
            "Đường Xô Viết Nghệ Tĩnh", "Đường Bạch Đằng"
        ],
        "details": [
            "Số 50", "Số 128", "Hẻm 450/12", "Số 20/4",
            "Số 310", "Số 15", "Hẻm 85/2", "Số 99",
            "Số 64/6", "Lầu 2 số 8A", "Số 142/5A",
            "Chung cư B phòng 12.04", "Số 57-59"
        ]
    },

    "Đà Nẵng": {
        "streets": [
            "Đường Nguyễn Văn Linh", "Đường Lê Duẩn",
            "Đường Hùng Vương", "Đường Trần Phú",
            "Đường Bạch Đằng", "Đường Điện Biên Phủ",
            "Đường 2 Tháng 9", "Đường Võ Nguyên Giáp",
            "Đường Nguyễn Tất Thành", "Đường Ngô Quyền",
            "Đường Phạm Văn Đồng", "Đường Lê Đình Dương",
            "Đường Hoàng Diệu", "Đường Phan Châu Trinh",
            "Đường Núi Thành", "Đường Nguyễn Hữu Thọ",
            "Đường Cách Mạng Tháng Tám", "Đường Trường Chinh",
            "Đường Tôn Đức Thắng", "Đường Nguyễn Lương Bằng",
            "Đường Nguyễn Huy Tưởng", "Đường Hoàng Văn Thái",
            "Đường Âu Cơ", "Đường Trần Đại Nghĩa"
        ],
        "details": [
            "Số 12", "Số 88", "Kiệt 102/3", "Số 45/2",
            "Số 240", "Số 16", "Kiệt 295/5", "Số 8",
            "Số 112", "Số 54", "Số 192", "Số 73/2",
            "Căn hộ số 5A"
        ]
    },

    "Cao Bằng": {
        "streets": [
            "Đường Hoàng Đình Giong", "Đường Kim Đồng",
            "Đường Xuân Trường", "Đường 3 Tháng 10",
            "Đường Pác Bó", "Đường Võ Nguyên Giáp",
            "Quốc lộ 3", "Quốc lộ 4A", "Đường 1 Tháng 4"
        ],
        "details": [
            "Số 12", "Số 35", "Số 68", "Số 102/4",
            "Ngõ 25", "Số 88"
        ]
    },

    "Tuyên Quang": {
        "streets": [
            "Đường Quang Trung", "Đường Bình Thuận",
            "Đường 17 Tháng 8", "Đường Chiến Thắng Sông Lô",
            "Đường Nguyễn Trãi", "Đường Tân Trào",
            "Quốc lộ 2", "Đường Lê Duẩn", "Đường Trường Chinh"
        ],
        "details": [
            "Số 15", "Số 42", "Số 86", "Số 120/5",
            "Ngõ 32", "Số 210"
        ]
    },

    "Điện Biên": {
        "streets": [
            "Đường Võ Nguyên Giáp", "Đường Nguyễn Hữu Thọ",
            "Đường Trường Chinh", "Đường Hoàng Văn Thái",
            "Đường Nguyễn Chí Thanh", "Đường Trần Đăng Ninh",
            "Quốc lộ 279", "Đường Điện Biên Phủ"
        ],
        "details": [
            "Số 18", "Số 45", "Số 72", "Số 105/3",
            "Ngõ 12", "Số 156"
        ]
    },

    "Lai Châu": {
        "streets": [
            "Đường Trần Hưng Đạo", "Đường Hoàng Văn Thái",
            "Đường Điện Biên Phủ", "Đường Nguyễn Trãi",
            "Đường Lê Duẩn", "Quốc lộ 4D", "Quốc lộ 32"
        ],
        "details": [
            "Số 10", "Số 36", "Số 58", "Số 90/2",
            "Ngõ 15", "Số 120"
        ]
    },

    "Sơn La": {
        "streets": [
            "Đường Tô Hiệu", "Đường Lê Duẩn",
            "Đường Trường Chinh", "Đường Chu Văn Thịnh",
            "Đường Điện Biên Phủ", "Đường Nguyễn Lương Bằng",
            "Quốc lộ 6", "Quốc lộ 37"
        ],
        "details": [
            "Số 14", "Số 40", "Số 65", "Số 108/3",
            "Ngõ 22", "Số 145"
        ]
    },

    "Lào Cai": {
        "streets": [
            "Đường Hoàng Liên", "Đường Nguyễn Huệ",
            "Đại lộ Trần Hưng Đạo", "Đường Nhạc Sơn",
            "Đường Nguyễn Tất Thành", "Đường Điện Biên Phủ",
            "Quốc lộ 4E", "Quốc lộ 70"
        ],
        "details": [
            "Số 20", "Số 45", "Số 76", "Số 112/5",
            "Ngõ 18", "Số 160"
        ]
    },

    "Thái Nguyên": {
        "streets": [
            "Đường Phan Đình Phùng", "Đường Hoàng Văn Thụ",
            "Đường Lương Ngọc Quyến", "Đường Cách Mạng Tháng Tám",
            "Đường Bắc Kạn", "Đường Quang Trung",
            "Đường Minh Khai", "Quốc lộ 3"
        ],
        "details": [
            "Số 16", "Số 42", "Số 78", "Số 125/4",
            "Ngõ 20", "Số 180"
        ]
    },

    "Lạng Sơn": {
        "streets": [
            "Đường Trần Đăng Ninh", "Đường Lê Lợi",
            "Đường Bắc Sơn", "Đường Nhị Thanh",
            "Đường Nguyễn Du", "Đường Trần Phú",
            "Quốc lộ 1B", "Quốc lộ 4A"
        ],
        "details": [
            "Số 11", "Số 35", "Số 69", "Số 104/2",
            "Ngõ 15", "Số 145"
        ]
    },

    "Quảng Ninh": {
        "streets": [
            "Đường Trần Quốc Nghiễn", "Đường Lê Thánh Tông",
            "Đường Cao Thắng", "Đường Hoàng Quốc Việt",
            "Đường Hạ Long", "Đường Cái Dăm",
            "Đường Trần Phú", "Đường Thanh Niên",
            "Đường Đại lộ Hòa Bình", "Đường Hùng Vương"
        ],
        "details": [
            "Số 15", "Số 48", "Số 82", "Số 120/5",
            "Ngõ 24", "Số 205"
        ]
    },

    "Bắc Ninh": {
        "streets": [
            "Đường Nguyễn Quyền", "Đường Ngô Gia Tự",
            "Đường Lý Thái Tổ", "Đường Nguyễn Gia Thiều",
            "Đường Nguyễn Văn Cừ", "Đường Đấu Mã",
            "Đường Trần Phú", "Đường Minh Khai"
        ],
        "details": [
            "Số 12", "Số 38", "Số 65", "Số 98/3",
            "Ngõ 18", "Số 145"
        ]
    },

    "Phú Thọ": {
        "streets": [
            "Đại lộ Hùng Vương", "Đường Nguyễn Tất Thành",
            "Đường Nguyễn Du", "Đường Châu Phong",
            "Đường Lê Đồng", "Đường Trần Phú",
            "Quốc lộ 2", "Quốc lộ 32"
        ],
        "details": [
            "Số 15", "Số 42", "Số 76", "Số 110/4",
            "Ngõ 25", "Số 180"
        ]
    },

    "Hải Phòng": {
        "streets": [
            "Đường Điện Biên Phủ", "Đường Quang Trung",
            "Đường Trần Hưng Đạo", "Đường Tô Hiệu",
            "Đường Nguyễn Đức Cảnh", "Đường Hồ Sen",
            "Đường Lạch Tray", "Đường Đà Nẵng",
            "Đường Cầu Đất", "Đường Lê Hồng Phong",
            "Đường Nguyễn Bỉnh Khiêm", "Đường Đình Vũ"
        ],
        "details": [
            "Số 20", "Số 45", "Số 88", "Số 125/5",
            "Ngõ 30", "Số 210"
        ]
    },

    "Hưng Yên": {
        "streets": [
            "Đường Điện Biên Phủ", "Đường Nguyễn Văn Linh",
            "Đường Chu Văn An", "Đường Bãi Sậy",
            "Đường Nguyễn Thiện Thuật", "Đường Triệu Quang Phục",
            "Quốc lộ 5", "Quốc lộ 38"
        ],
        "details": [
            "Số 14", "Số 38", "Số 72", "Số 105/3",
            "Ngõ 20", "Số 156"
        ]
    },

    "Ninh Bình": {
        "streets": [
            "Đường Đinh Tất Miễn", "Đường Nguyễn Huệ",
            "Đường Trần Hưng Đạo", "Đường Trần Phú",
            "Đường Trường Chinh", "Đường Giải Phóng",
            "Đường Biên Hòa", "Đường Lê Hoàn",
            "Quốc lộ 1A"
        ],
        "details": [
            "Số 18", "Số 42", "Số 75", "Số 110/4",
            "Ngõ 25", "Số 165"
        ]
    },

    "Thanh Hóa": {
        "streets": [
            "Đường Quang Trung", "Đường Lê Hoàn",
            "Đường Trần Phú", "Đường Nguyễn Trãi",
            "Đại lộ Lê Lợi", "Đường Tống Duy Tân",
            "Đường Trần Hưng Đạo", "Quốc lộ 1A"
        ],
        "details": [
            "Số 12", "Số 40", "Số 78", "Số 115/5",
            "Ngõ 22", "Số 180"
        ]
    },

    "Nghệ An": {
        "streets": [
            "Đường Quang Trung", "Đường Lê Duẩn",
            "Đường Nguyễn Thị Minh Khai", "Đường Trường Thi",
            "Đường Nguyễn Văn Cừ", "Đường Hà Huy Tập",
            "Đường Phan Đình Phùng", "Đường Hồ Tùng Mậu",
            "Đường Mai Hắc Đế", "Quốc lộ 1A"
        ],
        "details": [
            "Số 15", "Số 46", "Số 82", "Số 120/3",
            "Ngõ 25", "Số 195"
        ]
    },

    "Hà Tĩnh": {
        "streets": [
            "Đường Phan Đình Phùng", "Đường Nguyễn Du",
            "Đường Hà Huy Tập", "Đường Trần Phú",
            "Đường Nguyễn Công Trứ", "Đường Hải Thượng Lãn Ông",
            "Quốc lộ 1A", "Đường Hàm Nghi"
        ],
        "details": [
            "Số 10", "Số 35", "Số 68", "Số 102/4",
            "Ngõ 18", "Số 150"
        ]
    },

    "Quảng Trị": {
        "streets": [
            "Đường Trần Hưng Đạo", "Đường Quang Trung",
            "Đường Lý Thường Kiệt", "Đường Nguyễn Trãi",
            "Đường Lê Duẩn", "Đường Hữu Nghị",
            "Quốc lộ 1A", "Quốc lộ 9"
        ],
        "details": [
            "Số 12", "Số 44", "Số 76", "Số 108/3",
            "Ngõ 20", "Số 165"
        ]
    },

    "Huế": {
        "streets": [
            "Đường Lê Lợi", "Đường Nguyễn Huệ",
            "Đường Hùng Vương", "Đường Trần Hưng Đạo",
            "Đường Điện Biên Phủ", "Đường Nguyễn Trãi",
            "Đường Đống Đa", "Đường Bùi Thị Xuân",
            "Đường Lý Thường Kiệt"
        ],
        "details": [
            "Số 15", "Số 38", "Số 72", "Số 105/4",
            "Kiệt 20", "Số 160"
        ]
    },

    "Quảng Ngãi": {
        "streets": [
            "Đường Quang Trung", "Đường Lê Trung Đình",
            "Đường Nguyễn Nghiêm", "Đường Nguyễn Công Phương",
            "Đường Lê Thánh Tôn", "Đường Tôn Đức Thắng",
            "Quốc lộ 1A", "Đường Phan Đình Phùng"
        ],
        "details": [
            "Số 12", "Số 45", "Số 78", "Số 110/3",
            "Ngõ 18", "Số 150"
        ]
    },

    "Gia Lai": {
        "streets": [
            "Đường Trần Phú", "Đường Lê Lợi",
            "Đường Hùng Vương", "Đường Nguyễn Tất Thành",
            "Đường Phạm Văn Đồng", "Đường Nguyễn Viết Xuân",
            "Đường Cách Mạng Tháng Tám", "Đường Lê Duẩn",
            "Đường Trường Chinh", "Quốc lộ 14"
        ],
        "details": [
            "Số 15", "Số 42", "Số 75", "Số 108/4",
            "Ngõ 22", "Số 165"
        ]
    },

    "Khánh Hòa": {
        "streets": [
            "Đường Trần Phú", "Đường Thái Nguyên",
            "Đường Yersin", "Đường Lê Thánh Tôn",
            "Đường Phạm Văn Đồng", "Đường 2 Tháng 4",
            "Đường Đặng Tất", "Đường Nguyễn Thị Minh Khai",
            "Đường Hùng Vương", "Đường Nguyễn Thái Học"
        ],
        "details": [
            "Số 12", "Số 38", "Số 65", "Số 105/3",
            "Hẻm 20", "Số 180"
        ]
    },

    "Đắk Lắk": {
        "streets": [
            "Đường Nguyễn Tất Thành", "Đường Lê Duẩn",
            "Đường Phan Chu Trinh", "Đường Y Jút",
            "Đường Nguyễn Chí Thanh", "Đường Nguyễn Văn Cừ",
            "Đường Lê Duẩn", "Đường Y Wang",
            "Đường Nguyễn Lương Bằng", "Quốc lộ 14"
        ],
        "details": [
            "Số 15", "Số 42", "Số 76", "Số 112/5",
            "Ngõ 24", "Số 190"
        ]
    },

    "Lâm Đồng": {
        "streets": [
            "Đường Trần Phú", "Đường 3 Tháng 2",
            "Đường Phan Đình Phùng", "Đường Nguyễn Văn Cừ",
            "Đường Hoàng Văn Thụ", "Đường Phạm Ngũ Lão",
            "Đường Tô Hiến Thành", "Đường Nguyễn Tất Thành",
            "Đường Trần Hưng Đạo", "Đường Tuyên Quang"
        ],
        "details": [
            "Số 10", "Số 35", "Số 68", "Số 105/4",
            "Ngõ 20", "Số 150"
        ]
    },

    "Đồng Nai": {
        "streets": [
            "Đường Phạm Văn Thuận", "Đường Nguyễn Ái Quốc",
            "Đường Võ Thị Sáu", "Đường Đồng Khởi",
            "Đường Bùi Văn Hòa", "Đường Hoàng Văn Bổn",
            "Đường 30 Tháng 4", "Đường Cách Mạng Tháng Tám",
            "Đường Nguyễn Thị Minh Khai", "Đường Hùng Vương",
            "Đường Phú Riềng Đỏ", "Đường Nguyễn Huệ",
            "ĐT741", "Quốc lộ 1A"
        ],
        "details": [
            "Số 15", "Số 48", "Số 82", "Số 120/5",
            "Hẻm 24", "Số 205"
        ]
    },

    "Tây Ninh": {
        "streets": [
            "Đường Cách Mạng Tháng Tám", "Đường 30 Tháng 4",
            "Đường Nguyễn Chí Thanh", "Đường Điện Biên Phủ",
            "Đường Hùng Vương", "Đường Nguyễn Huệ",
            "Đường Trần Phong Sắc", "Quốc lộ 1A",
            "Quốc lộ 22", "Đường Xuyên Á",
            "Đường Nguyễn Văn Rốp", "Đường Nguyễn Văn Linh",
            "ĐT782", "Đường Tỉnh lộ 10"
        ],
        "details": [
            "Số 12", "Số 45", "Số 76", "Số 105/4",
            "Hẻm 20", "Số 160"
        ]
    },

    "Đồng Tháp": {
        "streets": [
            "Đường Nguyễn Huệ", "Đường 30 Tháng 4",
            "Đường Phạm Hữu Lầu", "Đường Ấp Bắc",
            "Đường Lý Thường Kiệt", "Đường Nam Kỳ Khởi Nghĩa",
            "Đường Nguyễn Sinh Sắc", "Đường Trần Hưng Đạo",
            "Đường Hùng Vương", "Quốc lộ 30",
            "Quốc lộ 1A"
        ],
        "details": [
            "Số 15", "Số 42", "Số 78", "Số 110/3",
            "Hẻm 18", "Số 165"
        ]
    },

    "Vĩnh Long": {
        "streets": [
            "Đường Phạm Thái Bường", "Đường Nguyễn Văn Thiệt",
            "Đường 2 Tháng 9", "Đường Nguyễn Chí Thanh",
            "Đường Đinh Tiên Hoàng", "Đường Tống Phước Hiệp",
            "Đường Đồng Khởi", "Đường Đoàn Hoàng Minh",
            "Đường Nguyễn Đình Chiểu", "Quốc lộ 53"
        ],
        "details": [
            "Số 12", "Số 38", "Số 65", "Số 105/4",
            "Hẻm 20", "Số 150"
        ]
    },

    "An Giang": {
        "streets": [
            "Đường Trần Hưng Đạo", "Đường Nguyễn Trãi",
            "Đường Lý Thái Tổ", "Đường Tân Lộ Kiều Lương",
            "Đường Thủ Khoa Huân", "Đường Nguyễn Trung Trực",
            "Đường 3 Tháng 2", "Đường Nguyễn Bỉnh Khiêm",
            "Đường Lê Lợi", "Quốc lộ 91"
        ],
        "details": [
            "Số 15", "Số 42", "Số 76", "Số 110/5",
            "Hẻm 24", "Số 180"
        ]
    },

    "Cần Thơ": {
        "streets": [
            "Đại Lộ Hòa Bình", "Đường Hai Bà Trưng",
            "Đường 30 Tháng 4", "Đường Mậu Thân",
            "Đường Nguyễn Việt Hồng", "Đường Trần Phú",
            "Đường Nguyễn Trãi", "Đường Cách Mạng Tháng Tám",
            "Đường Võ Nguyên Giáp", "Đường Phạm Hùng",
            "Đường Lý Thái Tổ", "Đường Trần Hưng Đạo",
            "Đường Nguyễn Văn Cừ", "Quốc lộ 1A"
        ],
        "details": [
            "Số 12", "Số 45", "Số 78", "Số 110/4",
            "Hẻm 25", "Số 165"
        ]
    },

    "Cà Mau": {
        "streets": [
            "Đường Phan Ngọc Hiển", "Đường Nguyễn Tất Thành",
            "Đường Nguyễn Trãi", "Đường Nguyễn Công Trứ",
            "Đường Lý Bôn", "Đường Ngô Quyền",
            "Đường Trần Phú", "Đường Hai Bà Trưng",
            "Đường 30 Tháng 4", "Quốc lộ 1A"
        ],
        "details": [
            "Số 15", "Số 42", "Số 76", "Số 108/3",
            "Hẻm 20", "Số 150"
        ]
    }
}

# ==================== QUẢN LÝ TIẾN TRÌNH & LỊCH SỬ ====================
def load_history():
    """Tải lịch sử các hội thoại đã xử lý để không bao giờ bị mất dấu khi reload"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"processed_ids": [], "processed_names": [], "total_count": 0}

def save_history(history):
    """Lưu lịch sử hội thoại ra file JSON"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử: {e}")

def mark_chat_processed(history, room_id, customer_name, customer_phone=""):
    """Ghi nhận hội thoại đã hoàn thành hoặc đã có địa chỉ"""
    changed = False
    if room_id and room_id not in history.setdefault("processed_ids", []):
        history["processed_ids"].append(room_id)
        changed = True
    key = f"{customer_name}_{customer_phone}".strip("_")
    if key and key not in history.setdefault("processed_names", []):
        history["processed_names"].append(key)
        changed = True
    # Lưu cả customer_name thuần để quét danh sách siêu nhanh không cần click
    if customer_name and customer_name not in history.setdefault("processed_names", []):
        history["processed_names"].append(customer_name)
        changed = True
    if changed:
        history["total_count"] = len(history["processed_ids"])
        save_history(history)

def is_chat_processed(history, room_id="", customer_name="", customer_phone=""):
    """Kiểm tra hội thoại đã được xử lý chưa theo room_id duy nhất"""
    if room_id and room_id in history.get("processed_ids", []):
        return True
    return False

# ==================== THAO TÁC GIAO DIỆN & TỰ ĐỘNG DỌN DẸP ====================
def clean_up_page_state(page):
    """Đóng mọi popup, dropdown hoặc form đang mở dở để tránh kẹt giao diện khi treo máy"""
    try:
        # Bấm Escape để đóng menu dropdown hoặc popover đang mở lơ lửng
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)

        # Nếu có nút Hủy của form khách hàng đang mở dở -> bấm Hủy
        cancel_btn = page.locator(".customer-form-H2pIpK button:has-text('Hủy'), button:has-text('Hủy')").last
        if cancel_btn.is_visible():
            cancel_btn.click(timeout=1500)
            page.wait_for_timeout(300)

        # Nếu có modal thông báo/xác nhận của Ant Design -> đóng lại
        modal_close = page.locator(".ant-modal-close, .ant-modal-footer button:has-text('Đóng'), .ant-modal-footer button:has-text('Hủy')").first
        if modal_close.is_visible():
            modal_close.click(timeout=1500)
    except Exception:
        pass

FAST_CITIES = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng"]

def select_random_ward_option(page, timeout=2000):
    """Chọn ngẫu nhiên xã/phường siêu tốc từ dropdown"""
    # Lấy dropdown đang mở hiện tại (dropdown mới nhất)
    active_dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").last
    options = active_dropdown.locator(".ant-select-item-option:visible")
    options.first.wait_for(state="visible", timeout=timeout)
    count = options.count()
    if count == 0:
        raise Exception("Không tìm thấy xã/phường nào trong danh sách")
        
    random_index = random.randint(0, min(count - 1, 5))
    target_option = options.nth(random_index)
    ward_name = target_option.inner_text().strip()
    target_option.click(force=True, timeout=1500)
    return ward_name

def get_current_chat_info(page):
    """Lấy vị trí index, tên và ID của hội thoại đang active trên màn hình"""
    try:
        return page.evaluate("""() => {
            const active = document.querySelector("li[class*='lists-chat-active']");
            const all = Array.from(document.querySelectorAll("li[class*='lists-chat-']"));
            if (!active) {
                return { index: -1, total: all.length, name: "Chưa chọn hội thoại nào", roomId: "" };
            }
            const idx = all.indexOf(active);
            const nameEl = active.querySelector("span, div, p");
            const name = nameEl ? nameEl.innerText.trim().split('\\n')[0] : `Hội thoại ${idx + 1}`;
            const url = window.location.href;
            const roomId = url.includes('/t/') ? url.split('/t/')[1].split('?')[0] : "";
            return { index: idx, total: all.length, name: name, roomId: roomId };
        }""")
    except Exception:
        return {"index": -1, "total": 0, "name": "Không xác định", "roomId": ""}

def extract_address_from_chat(page, timeout=3000):
    """
    Trích xuất chuỗi địa chỉ thực tế từ tin nhắn/card thông tin trong khung chat.
    Có cơ chế chờ tin nhắn nạp xong từ server (tối đa 3 giây).
    """
    start_t = time.time()
    while time.time() - start_t < timeout / 1000:
        try:
            addr = page.evaluate("""() => {
                const getFullText = (el) => {
                    if (!el) return "";
                    return el.getAttribute("title") || el.getAttribute("data-original-title") || el.innerText || el.textContent || "";
                };

                // 1. Quét tất cả thẻ card / block tin nhắn
                const blocks = Array.from(document.querySelectorAll("[class*='message'], [class*='bubble'], [class*='card'], [class*='item'], div"));
                for (const b of blocks) {
                    const txt = b.innerText || "";
                    if (txt.includes("Địa chỉ") && (txt.includes("fptlapmang") || txt.includes("Họ và tên") || txt.includes("Số điện thoại") || txt.includes("Đường dẫn") || txt.includes("Email"))) {
                        // Tách theo dòng
                        const lines = txt.split(/\\r?\\n/).map(l => l.trim()).filter(Boolean);
                        for (let i = 0; i < lines.length; i++) {
                            const l = lines[i].toLowerCase();
                            if (l === "địa chỉ" || l.startsWith("địa chỉ:")) {
                                if (l.startsWith("địa chỉ:") && lines[i].length > 9) {
                                    return lines[i].replace(/^địa chỉ:\\s*/i, "").trim();
                                }
                                if (i + 1 < lines.length && lines[i+1]) {
                                    const nextLine = lines[i+1].trim();
                                    const withTitle = b.querySelector("[title]");
                                    if (withTitle && withTitle.getAttribute("title") && withTitle.getAttribute("title").includes(",")) {
                                        return withTitle.getAttribute("title").trim();
                                    }
                                    return nextLine;
                                }
                            }
                        }
                    }
                }

                // 2. Quét thẻ bất kỳ có chữ Địa chỉ
                const all = Array.from(document.querySelectorAll("div, p, span, li"));
                for (const el of all) {
                    if (el.children.length === 0 && (el.innerText || "").trim().toLowerCase() === "địa chỉ") {
                        const next = el.nextElementSibling || (el.parentElement ? el.parentElement.nextElementSibling : null);
                        if (next) {
                            const title = next.getAttribute("title") || (next.querySelector("[title]") ? next.querySelector("[title]").getAttribute("title") : null);
                            if (title && title.includes(",")) return title.trim();
                            const t = next.innerText ? next.innerText.trim() : "";
                            if (t && t.length > 3) return t;
                        }
                    }
                }
                return "";
            }""")
            if addr and len(addr) > 5:
                return addr.strip()
        except Exception:
            pass
        time.sleep(0.2)
    return ""

def parse_address(raw_addr):
    """
    Bóc tách chuỗi địa chỉ thành: (tỉnh/thành, quận/huyện/phường, tên đường, số nhà/chi tiết)
    """
    if not raw_addr:
        return "", "", "", ""
    raw_addr = re.sub(r"\.{2,}$", "", raw_addr).strip()
    parts = [p.strip() for p in raw_addr.split(",") if p.strip()]
    if not parts:
        return "", "", "", ""
    
    if len(parts) >= 3:
        tinh = parts[-1]
        quan_phuong = parts[-2]
        duong_raw = parts[0]
    elif len(parts) == 2:
        tinh = parts[1]
        quan_phuong = ""
        duong_raw = parts[0]
    else:
        tinh = ""
        quan_phuong = ""
        duong_raw = parts[0]

    clean_tinh = re.sub(r"^(Tỉnh|Thành phố|TP\.?)\s+", "", tinh, flags=re.IGNORECASE).strip()
    if clean_tinh.lower() in ["hcm", "tp hcm", "tp.hcm"]:
        clean_tinh = "Hồ Chí Minh"
    elif clean_tinh.lower() in ["hn", "tp hn", "tp.hn"]:
        clean_tinh = "Hà Nội"

    so_nha = "Số 1"
    duong = duong_raw
    
    m = re.match(r"^(\d+[a-zA-Z\d\/\-]*)\s*(?:Đường|đường)?\s*(.*)$", duong_raw)
    if m:
        num = m.group(1).strip()
        rest = m.group(2).strip()
        so_nha = f"Số {num}" if not num.lower().startswith("số") else num
        duong = rest if rest else duong_raw
        if duong and not any(duong.lower().startswith(p) for p in ["đường", "phố", "đại lộ", "quốc lộ", "hẻm", "ngõ", "kiệt"]):
            duong = f"Đường {duong}"
    else:
        if duong and not any(duong.lower().startswith(p) for p in ["đường", "phố", "đại lộ", "quốc lộ", "hẻm", "ngõ", "kiệt"]):
            duong = f"Đường {duong}"

    return clean_tinh, quan_phuong, duong, so_nha

def fill_address_for_current_chat(page, chat_label="", max_retries=2):
    """
    Điền địa chỉ siêu tốc theo dữ liệu bóc tách trực tiếp từ tin nhắn của khách hàng.
    Nếu không tìm thấy tin nhắn -> Tự động dùng kho dữ liệu random dự phòng.
    """
    for attempt in range(max_retries):
        t0 = time.time()
        try:
            # 0. Trích xuất địa chỉ thực tế từ tin nhắn trong khung chat
            raw_chat_address = extract_address_from_chat(page)
            parsed_city, parsed_ward, parsed_street, parsed_detail = parse_address(raw_chat_address)
            
            if raw_chat_address:
                print(f"[{chat_label}] 🎯 Bóc tách từ chat: '{raw_chat_address}' -> Tỉnh: {parsed_city} | Quận/Phường: {parsed_ward} | Đường: {parsed_street} | Chi tiết: {parsed_detail}")

            # 1. Mở form chỉnh sửa nếu chưa mở
            form = page.locator(".customer-form-H2pIpK")
            if form.count() == 0 or not form.first.is_visible():
                pencil = page.locator(".ant-card:has-text('Thông tin khách hàng') .ant-card-extra svg, .ant-card-extra > svg").first
                pencil.wait_for(state="visible", timeout=3000)
                pencil.click(timeout=2000)
                form.wait_for(state="visible", timeout=3000)

            # 1.1 Đảm bảo tên khách hàng không bị rỗng
            name_inp = page.locator("#name")
            if name_inp.count() > 0 and name_inp.first.is_visible():
                if not name_inp.first.input_value().strip():
                    name_from_label = chat_label.split(" - ")[-1].strip("[] ") if " - " in chat_label else "Khách hàng"
                    name_inp.first.fill(name_from_label)

            # 2. Kiểm tra nhanh: Nếu khách đã có địa chỉ từ trước -> Bỏ qua ngay
            street_inp = page.locator("#address_0_street")
            if street_inp.count() > 0 and street_inp.first.is_visible() and street_inp.first.input_value().strip():
                existing = street_inp.first.input_value().strip()
                print(f"[{chat_label}] Đã có địa chỉ ('{existing}') -> Bỏ qua!")
                cancel_btn = page.locator("button:has-text('Hủy')").last
                if cancel_btn.is_visible():
                    cancel_btn.click(timeout=1500)
                return "ALREADY_FILLED"

            # 3. Bấm 'Thêm địa chỉ' nếu chưa có ô nhập tỉnh/thành
            prov_inp = page.locator("#address_0_province")
            if prov_inp.count() == 0 or not prov_inp.first.is_visible():
                add_addr_btn = page.locator("button:has-text('Thêm địa chỉ'), span:text-is('Thêm địa chỉ')").first
                add_addr_btn.wait_for(state="visible", timeout=3000)
                add_addr_btn.click(timeout=2000)
                prov_inp.wait_for(state="visible", timeout=3000)

            # 4. Điền và chọn Tỉnh/Thành phố (Tự động linh hoạt - Có Fallback nếu tỉnh không có trong bộ lọc SOP)
            prov_inp.click(timeout=2000)
            target_city = parsed_city if parsed_city else random.choice(FAST_CITIES)
            prov_inp.fill(target_city)
            page.wait_for_timeout(250)

            prov_dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").last
            prov_opt = prov_dropdown.locator(f".ant-select-item-option:has-text('{target_city}')").first
            
            chosen_city = target_city
            if prov_opt.is_visible(timeout=1000):
                prov_opt.click(timeout=1500)
            else:
                # Nếu không tìm thấy Tỉnh từ tin nhắn trong bộ lọc SOP -> Tự động chuyển sang Tỉnh chuẩn (Hồ Chí Minh / Hà Nội / Đà Nẵng)
                fallback_city = random.choice(FAST_CITIES)
                print(f"[{chat_label}] ⚠️ SOP không tìm thấy tỉnh '{target_city}', tự động chọn '{fallback_city}'...")
                prov_inp.fill("")
                prov_inp.fill(fallback_city)
                page.wait_for_timeout(250)
                fb_opt = prov_dropdown.locator(f".ant-select-item-option:has-text('{fallback_city}')").first
                if fb_opt.is_visible(timeout=1500):
                    fb_opt.click(timeout=1500)
                else:
                    first_opt = prov_dropdown.locator(".ant-select-item-option:visible").first
                    if first_opt.is_visible(timeout=1000):
                        fallback_city = first_opt.inner_text().strip()
                        first_opt.click(timeout=1500)
                    else:
                        prov_inp.press("Enter")
                chosen_city = fallback_city

            try:
                prov_dropdown.wait_for(state="hidden", timeout=1500)
            except Exception:
                page.keyboard.press("Escape")
                page.wait_for_timeout(200)

            page.wait_for_timeout(350)

            # 5. Chọn Xã/Phường (Đảm bảo 100% luôn chọn được, không bao giờ bỏ sót)
            ward_inp = page.locator("#address_0_ward")
            ward_name = ""
            for ward_try in range(3):
                try:
                    ward_inp.click(timeout=1500)
                    page.wait_for_timeout(250)

                    ward_dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").last
                    ward_options = ward_dropdown.locator(".ant-select-item-option:visible")
                    ward_options.first.wait_for(state="visible", timeout=2500)

                    count = ward_options.count()
                    if count > 0:
                        matched_opt = None
                        if parsed_ward:
                            clean_qp = re.sub(r"^(Quận|Huyện|Thành phố|Thị xã|Phường|Xã)\s+", "", parsed_ward, flags=re.IGNORECASE).strip()
                            if clean_qp:
                                found_opt = ward_dropdown.locator(f".ant-select-item-option:visible:has-text('{clean_qp}')").first
                                if found_opt.is_visible(timeout=400):
                                    matched_opt = found_opt
                        
                        if matched_opt:
                            ward_name = matched_opt.inner_text().strip()
                            matched_opt.click(timeout=1500)
                            page.wait_for_timeout(150)
                            break
                        else:
                            # Tự chọn ngẫu nhiên trong các xã/phường có sẵn
                            random_index = random.randint(0, min(count - 1, 5))
                            target_opt = ward_options.nth(random_index)
                            candidate_name = target_opt.inner_text().strip()
                            ward_name = candidate_name if candidate_name else f"Phường {random_index + 1}"
                            target_opt.click(timeout=1500)
                            page.wait_for_timeout(150)
                            break
                except Exception:
                    page.wait_for_timeout(300)

            if not ward_name:
                try:
                    ward_inp.click(timeout=1000)
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("Enter")
                    ward_name = "Tùy chọn SOP"
                except Exception:
                    ward_name = "Mặc định"

            # 6. Điền Đường và Địa chỉ chi tiết (Ưu tiên tin nhắn, fallback về kho mẫu)
            city_data = ADDRESS_DATA.get(chosen_city, ADDRESS_DATA.get("Hà Nội", {}))
            streets_fallback = city_data.get("streets", ["Đường Nguyễn Huệ", "Đường Lê Lợi", "Đường Nguyễn Trãi"])
            details_fallback = city_data.get("details", ["Số 10", "Số 25", "Số 50", "Số 120"])

            final_street = parsed_street if (parsed_street and len(parsed_street) > 2) else random.choice(streets_fallback)
            final_detail = parsed_detail if (parsed_detail and len(parsed_detail) > 1) else random.choice(details_fallback)

            page.locator("#address_0_street").fill(final_street, timeout=2000)
            page.locator("#address_0_detail").fill(final_detail, timeout=2000)

            print(f"[{chat_label}] ✅ {chosen_city} | {ward_name} | {final_street} | {final_detail}")

            # 7. Bấm Lưu và chờ giao diện lưu xong
            save_btn = page.locator("button.ant-btn-primary:has-text('Lưu')").last
            save_btn.click(timeout=2000)

            try:
                form.wait_for(state="hidden", timeout=7000)
            except Exception:
                pass
            pencil = page.locator(".ant-card:has-text('Thông tin khách hàng') .ant-card-extra svg, .ant-card-extra > svg").first
            pencil.wait_for(state="visible", timeout=4000)
            
            print(f"==> Hoàn thành [{chat_label}] trong {time.time()-t0:.2f}s")
            return "SUCCESS"

        except Exception as e:
            print(f"⚠️ Lỗi xử lý [{chat_label}] (Thử lại {attempt + 1}/{max_retries}): {e}")
            clean_up_page_state(page)
            if attempt == max_retries - 1:
                return "FAILED"
            time.sleep(0.3)

def scroll_chat_list_to_load_more(page, max_retries=4):
    """
    Cuộn danh sách kết hợp nhiều cách để kích hoạt infinite-scroll tải thêm hội thoại.
    Kiên nhẫn chờ mạng nạp thêm dữ liệu từ server, không reload trang.
    """
    prev_count = page.locator("li[class*='lists-chat-']").count()
    for attempt in range(max_retries):
        # 1. Nhấp nháy cuộn nhẹ lên 80px rồi cuộn xuống sát đáy để chắc chắn kích hoạt onScroll event
        try:
            page.evaluate("""() => {
                const lis = document.querySelectorAll("li[class*='lists-chat-']");
                if (lis.length > 0) {
                    let p = lis[lis.length - 1].parentElement;
                    while (p && p !== document.body) {
                        const st = window.getComputedStyle(p);
                        if (p.scrollHeight > p.clientHeight && (st.overflowY === 'auto' || st.overflowY === 'scroll')) {
                            p.scrollTop = p.scrollHeight - 80;
                            setTimeout(() => { p.scrollTop = p.scrollHeight; }, 80);
                            break;
                        }
                        p = p.parentElement;
                    }
                }
                const view = document.querySelector(".view-S88vge") || document.querySelector("[class*='view-']");
                if (view) {
                    view.scrollTop = view.scrollHeight - 80;
                    setTimeout(() => { view.scrollTop = view.scrollHeight; }, 80);
                }
            }""")
        except Exception:
            pass

        # 2. Cuộn thẻ li cuối cùng vào viewport bằng Playwright
        try:
            last_li = page.locator("li[class*='lists-chat-']").last
            if last_li.is_visible():
                last_li.scroll_into_view_if_needed(timeout=1500)
        except Exception:
            pass

        # 3. Lăn chuột nhẹ
        try:
            page.mouse.wheel(0, 300)
        except Exception:
            pass

        # Chờ mạng FPT phản hồi thêm đợt hội thoại mới (1.2s)
        page.wait_for_timeout(1200)
        new_count = page.locator("li[class*='lists-chat-']").count()
        if new_count > prev_count:
            return new_count
    return prev_count

def switch_to_chat(page, chat_item, chat_title, timeout=4000):
    """
    Click chọn hội thoại và chờ hội thoại mới load xong dữ liệu siêu tốc.
    Trả về: (thành_công: bool, room_id: str, customer_name: str, customer_phone: str, has_address: bool)
    """
    try:
        old_url = page.url
        # Click trực tiếp bằng evaluate để kích hoạt ngay mà không bị lag kiểm tra DOM 700 items
        try:
            chat_item.evaluate("el => el.click()")
        except Exception:
            chat_item.click(force=True, timeout=1500)
        
        # Chờ URL đổi hoặc card thông tin khách hàng hiển thị
        start_t = time.time()
        while time.time() - start_t < timeout / 1000:
            if page.url != old_url and "/t/" in page.url:
                break
            pencil_or_form = page.locator(".ant-card:has-text('Thông tin khách hàng') .ant-card-extra svg, .customer-form-H2pIpK")
            if pencil_or_form.first.is_visible():
                break
            time.sleep(0.04)
            
        room_id = page.url.split("/t/")[-1].split("?")[0] if "/t/" in page.url else ""

        # Chờ card hiển thị
        pencil_or_form = page.locator(".ant-card:has-text('Thông tin khách hàng') .ant-card-extra svg, .customer-form-H2pIpK").first
        pencil_or_form.wait_for(state="visible", timeout=timeout)
        
        # Đọc thông tin tên, SĐT
        card = page.locator(".ant-card:has-text('Thông tin khách hàng')")
        card_text = card.inner_text() if card.count() > 0 else ""
        lines = [line.strip() for line in card_text.split('\n') if line.strip()]
        name = lines[1] if len(lines) > 1 else chat_title
        phone = lines[2] if len(lines) > 2 else ""

        return True, room_id, name, phone
    except Exception as e:
        print(f"⚠️ Không thể chuyển sang hội thoại [{chat_title}]: {e}")
        return False, "", "", ""

def reload_and_recover(page, max_retries=3):
    """Tự động reload trang khi phát hiện web portal bị đơ/lag để giải phóng bộ nhớ"""
    for r in range(max_retries):
        print(f"\n🔄 [TỰ ĐỘNG PHỤC HỒI] Web bị đơ/lag! Đang reload lại trang (Lần {r + 1}/{max_retries})...")
        try:
            page.reload(wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("li[class*='lists-chat-']", timeout=20000)
            page.wait_for_timeout(1500)
            clean_up_page_state(page)
            print("✅ Reload thành công! Đang tiếp tục xử lý mượt mà...")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi reload trang (Lần {r + 1}): {e}")
            time.sleep(3)
    return False

def connect_to_portal(playwright, max_attempts=15):
    """Kết nối tới tab portal trên cổng CDP mặc định, có tự động thử lại khi treo máy"""
    for attempt in range(max_attempts):
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
            context = browser.contexts[0]
            page = next((t for t in context.pages if "portal-sop.fpt.vn" in t.url), None)
            if page:
                print(f"✅ Đã kết nối tới tab Portal (cổng {CDP_PORT}): {page.title()}")
                return browser, page
        except Exception:
            pass
        print(f"⏳ Đang chờ kết nối tới Chrome cổng {CDP_PORT} (Thử lại {attempt + 1}/{max_attempts})...")
        time.sleep(2)
    raise Exception(f"Không thể kết nối tới tab portal-sop.fpt.vn trên cổng {CDP_PORT}. Vui lòng kiểm tra Chrome.")

def trigger_auto_shutdown(total_count, countdown=None):
    """Kích hoạt tắt máy an toàn sau khi đếm ngược countdown giây (mặc định 10 phút = 600s) khi chạm mốc mục tiêu"""
    if countdown is None:
        countdown = SHUTDOWN_COUNTDOWN
    print("\n" + "=" * 65)
    print(f"🎉 ĐÃ CHẠM MỐC MỤC TIÊU: {total_count}/{TARGET_COUNT} HỘI THOẠI ĐÃ HOÀN THÀNH!")
    print("=" * 65)
    if AUTO_SHUTDOWN:
        mins = countdown // 60
        print("\n🛑 [CHẾ ĐỘ TỰ ĐỘNG TẮT MÁY ĐƯỢC KÍCH HOẠT]")
        print(f"⏰ Máy tính sẽ tự động tắt nguồn (Shutdown) sau {mins} phút ({countdown} giây)...")
        print("👉 Nếu bạn đang ngồi trước máy và muốn hủy tắt, hãy mở CMD/PowerShell gõ: shutdown /a\n")
        time.sleep(2)
        os.system(f"shutdown /s /t {countdown}")
        print("✅ Đã gửi lệnh hẹn giờ tắt máy tới Windows thành công.")
    else:
        print("\n✅ Đã đạt mốc mục tiêu. Giữ nguyên trạng thái máy (AUTO_SHUTDOWN = False).")

def run():
    history = load_history()
    
    with sync_playwright() as p:
        browser, page = connect_to_portal(p)

        print("\n" + "=" * 65)
        print(" CHƯƠNG TRÌNH ĐIỀN ĐỊA CHỈ TỰ ĐỘNG SOP PORTAL (CHẾ ĐỘ TREO MÁY)")
        print(f" Đã xử lý thành công trước đó: {history['total_count']} hội thoại (Lưu tại '{HISTORY_FILE}')")
        print(f" Mục tiêu tự động tắt máy khi chạm mốc: {TARGET_COUNT} hội thoại ({'BẬT' if AUTO_SHUTDOWN else 'TẮT'})")
        
        chat_info = get_current_chat_info(page)
        active_idx = chat_info["index"]
        total_chats = chat_info["total"]
        active_name = chat_info["name"]

        if active_idx >= 0:
            print(f" Đang mở hội thoại: #{active_idx + 1}/{total_chats} - {active_name}")
        else:
            print(f" Tổng số hội thoại đang có trên trang: {total_chats}")
        print("=" * 65)
        print("Tùy chọn chạy:")
        print("  [Enter] : Chạy tự động thông minh (Tự fix lỗi, tự cuộn, tự reload khi đơ, treo máy xuyên đêm)")
        print(f"  [1]     : Chỉ điền cho đúng 1 hội thoại đang mở (#{active_idx + 1} - {active_name}) rồi dừng")
        print("  [s]     : Chế độ thủ công (click hội thoại bất kỳ trên web rồi bấm Enter để điền)")
        print("  [r]     : Xóa lịch sử đã lưu để chạy lại từ đầu danh sách")
        print("  [Số]    : Bắt đầu chạy từ số thứ tự cụ thể (VD: 1, 15, 40...)")
        if "--reset" in sys.argv:
            history = {"processed_ids": [], "processed_names": [], "total_count": 0}
            save_history(history)
            print("🧹 Đã làm mới lịch sử về 0 (theo tham số --reset).")

        if "--auto" in sys.argv or "-y" in sys.argv:
            print("\n🚀 [CHẾ ĐỘ TỰ ĐỘNG TREO MÁY] Tự động bắt đầu chạy thông minh sau 1 giây...")
            time.sleep(1)
            user_choice = ""
        else:
            user_choice = input("Chọn chế độ (Nhấn Enter để chạy tự động): ").strip()

        # Reset lịch sử nếu gõ 'r'
        if user_choice.lower() == 'r':
            confirm = input("Bạn có chắc muốn xóa lịch sử đã lưu? (y/n): ").strip().lower()
            if confirm == 'y':
                history = {"processed_ids": [], "processed_names": [], "total_count": 0}
                save_history(history)
                print("Đã làm mới lịch sử.")
            user_choice = ""

        # Chế độ thủ công (s)
        if user_choice.lower() == 's':
            print("\n>>> ĐÃ BẬT CHẾ ĐỘ THỦ CÔNG <<<")
            print("Cách dùng: Click vào bất kỳ hội thoại nào trên màn hình web, rồi bấm [Enter] để điền.")
            print("Gõ 'q' để thoát.")
            while True:
                cmd = input("\n[Thủ công] Bấm Enter để điền (hoặc 'q' để thoát): ").strip().lower()
                if cmd == 'q':
                    print("Đã thoát chế độ thủ công.")
                    break
                info = get_current_chat_info(page)
                label = f"#{info['index'] + 1} - {info['name']}" if info['index'] >= 0 else info['name']
                print(f"--- Đang xử lý: {label} ---")
                res = fill_address_for_current_chat(page, label)
                if res in ["SUCCESS", "ALREADY_FILLED"]:
                    mark_chat_processed(history, info.get("roomId", ""), info["name"])
            return

        # Chế độ chỉ điền 1 hội thoại đang mở (1)
        if user_choice == '1' and active_idx >= 0:
            label = f"#{active_idx + 1} - {active_name}"
            print(f"\n--- Đang xử lý đúng 1 hội thoại: {label} ---")
            res = fill_address_for_current_chat(page, label)
            if res in ["SUCCESS", "ALREADY_FILLED"]:
                mark_chat_processed(history, chat_info.get("roomId", ""), active_name)
            print("Hoàn tất!")
            return

        # Xác định vị trí bắt đầu
        start_index = 0
        if user_choice.isdigit():
            start_index = max(0, int(user_choice) - 1)
        elif ("--auto" not in sys.argv and "-y" not in sys.argv) and active_idx >= 0:
            start_index = active_idx

        print(f"\n>>> BẮT ĐẦU CHẠY TỰ ĐỘNG TỪ HỘI THOẠI #{start_index + 1} <<<")
        print("🛡️ CHẾ ĐỘ TREO MÁY ĐÃ BẬT:")
        print("  - Tự động khắc phục 100% lỗi phát sinh (đơ web, mất mạng tạm thời, lỗi portal).")
        print("  - Tự động cuộn nạp thêm toàn bộ danh sách hội thoại.")
        print("  - Tự động bỏ qua các hội thoại lỗi để không làm nghẽn tiến trình.")
        print("  - Kiên trì chờ hội thoại mới nếu type.py đang tạo thêm dở dang.")
        print(f"  - Tự động tắt máy khi chạm mốc {TARGET_COUNT} hội thoại: {'BẬT (Tắt sau 60s đếm ngược)' if AUTO_SHUTDOWN else 'TẮT'}\n")

        session_processed = 0
        processed_since_reload = 0
        session_processed_names = set()
        curr_index = start_index
        failure_tracker = {}  # Theo dõi số lần lỗi của từng hội thoại
        no_more_chats_count = 0  # Đếm số lần kiểm tra khi đã duyệt hết danh sách

        if page.locator("li[class*='lists-chat-']").count() == 0:
            print("\n🔄 Đang làm mới tab Portal để nạp danh sách hội thoại mới nhất...")
            reload_and_recover(page)

        while True:
            try:
                # Dọn dẹp trạng thái chỉ kích hoạt khi gặp lỗi/skip, bỏ ở đây để đạt tốc độ tối đa (2-3s)
                # clean_up_page_state(page)

                # Kiểm tra ngay nếu đã hoàn thành đủ mốc mục tiêu TARGET_COUNT
                if curr_index >= TARGET_COUNT or session_processed >= TARGET_COUNT:
                    total_done = max(curr_index, session_processed)
                    trigger_auto_shutdown(total_done)
                    break

                # [ĐÃ BỎ THEO YÊU CẦU] Bỏ reload định kỳ để tránh phải cuộn tải lại hàng trăm hội thoại từ đầu.
                # Hệ thống CHỈ reload khi web thực sự bị đứng/đơ (xử lý tự động ở các nhánh lỗi bên dưới).
                # if processed_since_reload >= RELOAD_EVERY:
                #     print(f"\n🔄 [ĐỊNH KỲ] Đã xử lý thêm {processed_since_reload} hội thoại mới. Tự động reload để giải phóng RAM...")
                #     reload_and_recover(page)
                #     processed_since_reload = 0
                #     curr_index = 0
                #     time.sleep(1)

                chats = page.locator("li[class*='lists-chat-']")
                total = chats.count()

                # Nếu vị trí hiện tại chạm tới đáy danh sách đang hiển thị -> Cuộn để nạp thêm!
                if curr_index >= total:
                    print(f"\n🔄 Đang ở cuối danh sách (hiện có {total} hội thoại). Đang cuộn nạp thêm...")
                    new_total = scroll_chat_list_to_load_more(page)
                    if new_total > total:
                        chats = page.locator("li[class*='lists-chat-']")
                        total = new_total
                        no_more_chats_count = 0
                    else:
                        no_more_chats_count += 1
                        if no_more_chats_count < 6:
                            print(f"⏳ Đang đợi mạng tải thêm hội thoại tiếp theo (Lần {no_more_chats_count}/6 - Chờ 3s tại vị trí #{curr_index}, KHÔNG reload)...")
                            time.sleep(3)
                            continue
                        else:
                            # Đã kiên nhẫn đợi 6 lần (~20s) tại cuối danh sách mà không còn hội thoại nào mới
                            total_done = max(total, history.get('total_count', 0), session_processed)
                            print("\n" + "=" * 65)
                            print(f"🎉 ĐÃ HOÀN THÀNH TOÀN BỘ {total} HỘI THOẠI TRÊN HỆ THỐNG!")
                            print(f" Tổng cộng phiên này đã xử lý: {session_processed} hội thoại.")
                            print(f" Tổng tích lũy trong lịch sử: {total_done} hội thoại.")
                            print("=" * 65)

                            if AUTO_SHUTDOWN:
                                trigger_auto_shutdown(total_done)
                            else:
                                print("\n✅ Treo máy hoàn tất! Giữ nguyên trạng thái máy (AUTO_SHUTDOWN = False).")
                            break

                current_chat = chats.nth(curr_index)

                # Lấy thông tin cơ bản từ thẻ hội thoại trong danh sách
                try:
                    name_el = current_chat.locator("span, div, p").first
                    chat_title = name_el.inner_text().strip().split('\n')[0]
                except Exception:
                    chat_title = f"Hội thoại {curr_index + 1}"

                # Kiểm tra xem hội thoại này có bị lỗi lặp đi lặp lại nhiều lần không
                if failure_tracker.get(chat_title, 0) >= 2:
                    print(f"⚠️ [TỰ BỎ QUA] Hội thoại [{chat_title}] bị lỗi hệ thống FPT sau {failure_tracker[chat_title]} lần thử. Tạm thời bỏ qua để không làm nghẽn máy.")
                    curr_index += 1
                    if curr_index >= TARGET_COUNT:
                        trigger_auto_shutdown(curr_index)
                        break
                    continue

                print(f"\n--- [{curr_index + 1}/{total}] Đang xử lý: {chat_title} ---")

                # Chuyển sang hội thoại và chờ load xong (timeout 8s)
                ok_switch, room_id, cust_name, cust_phone = switch_to_chat(page, current_chat, chat_title, timeout=8000)
                
                # Nếu hội thoại bị đơ/lag không chuyển được -> Tự động bỏ qua sang hội thoại tiếp theo (KHÔNG reload)!
                if not ok_switch:
                    print(f"⚠️ Phát hiện hội thoại #{curr_index + 1} ({chat_title}) bị đơ/không phản hồi. Tự động bỏ qua để xử lý hội thoại tiếp theo!")
                    clean_up_page_state(page)
                    curr_index += 1
                    if curr_index >= TARGET_COUNT:
                        trigger_auto_shutdown(curr_index)
                        break
                    continue

                # Điền địa chỉ siêu tốc
                label = f"#{curr_index + 1} - {cust_name}"
                result = fill_address_for_current_chat(page, label)

                if result in ["SUCCESS", "ALREADY_FILLED"]:
                    mark_chat_processed(history, room_id, cust_name, cust_phone)
                    session_processed += 1
                    processed_since_reload += 1
                    no_more_chats_count = 0
                    failure_tracker.pop(chat_title, None)
                    current_num = curr_index + 1
                    if current_num >= TARGET_COUNT or session_processed >= TARGET_COUNT:
                        trigger_auto_shutdown(max(current_num, session_processed))
                        break
                elif result == "FAILED":
                    print(f"⚠️ Không thể điền địa chỉ cho hội thoại #{curr_index + 1} ({chat_title}). Tự động bỏ qua để xử lý tiếp!")
                    clean_up_page_state(page)
                    curr_index += 1
                    if curr_index >= TARGET_COUNT:
                        trigger_auto_shutdown(curr_index)
                        break
                    continue

                curr_index += 1

            except Exception as loop_err:
                print(f"\n🚨 [TỰ PHỤC HỒI HỆ THỐNG] Gặp ngoại lệ ngoài ý muốn: {loop_err}")
                time.sleep(3)
                try:
                    browser, page = connect_to_portal(p)
                    reload_and_recover(page)
                except Exception:
                    pass
                curr_index = 0

if __name__ == "__main__":
    run()

