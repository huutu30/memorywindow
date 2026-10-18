const fs = require('fs');
const path = require('path');

const host = 'fptwifitocdo.com';
const key = '8a2f4c9e1b3d'; // Mã xác minh của bạn
const keyLocation = `https://${host}/${key}.txt`;

// 1. Danh sách URL tĩnh của dự án
const staticPaths = [
  '',
  '/internet/ca-nhan',
  '/internet/gia-dinh',
  '/internet/game-thu',
  '/internet/doanh-nghiep',
  '/internet/wifi-7',
  '/giai-tri/fpt-play',
  '/thiet-bi/camera',
  '/thiet-bi/smarthome',
  '/tin-tuc',
  '/lien-he',
  '/chinh-sach-bao-mat',
  '/gioi-thieu',
  '/lien-ket-thanh-vien',
  '/khach-hang-doi-tac',
  '/tap-doan-fpt',
  '/so-do-trang-web',
];

const urls = new Set(staticPaths.map(p => `https://${host}${p}`));

// 2. Tự động đọc và trích xuất URL sản phẩm (/internet/[slug])
try {
  const productsDir = path.join(__dirname, 'data', 'products');
  if (fs.existsSync(productsDir)) {
    const files = fs.readdirSync(productsDir);
    files.forEach(file => {
      if (file.endsWith('.js')) {
        const content = fs.readFileSync(path.join(productsDir, file), 'utf8');
        const regex = /id:\s*["']([^"']+)["']/g;
        let match;
        while ((match = regex.exec(content)) !== null) {
          const productId = match[1];
          if (/^[a-z0-9-]+$/.test(productId)) {
            urls.add(`https://${host}/internet/${productId}`);
          }
        }
      }
    });
  }
} catch (e) {
  console.error('❌ Lỗi khi đọc thư mục sản phẩm:', e.message);
}

// 3. Tự động đọc và trích xuất bài viết tin tức (/tin-tuc/[slug])
try {
  const newsFile = path.join(__dirname, 'data', 'newsData.js');
  if (fs.existsSync(newsFile)) {
    const content = fs.readFileSync(newsFile, 'utf8');
    const regex = /"slug":\s*["']([^"']+)["']/g;
    let match;
    while ((match = regex.exec(content)) !== null) {
      urls.add(`https://${host}/tin-tuc/${match[1]}`);
    }
  }
} catch (e) {
  console.error('❌ Lỗi khi đọc file tin tức:', e.message);
}

// 4. Tự động đọc và trích xuất URL của các tỉnh thành (/dang-ky-internet-wifi/[city])
try {
  const cityFile = path.join(__dirname, 'data', 'cityData.js');
  if (fs.existsSync(cityFile)) {
    const content = fs.readFileSync(cityFile, 'utf8');
    const regex = /^\s*"([a-z0-9-]+)"\s*:\s*\{/gm;
    let match;
    while ((match = regex.exec(content)) !== null) {
      urls.add(`https://${host}/dang-ky-internet-wifi/${match[1]}`);
    }
  }
} catch (e) {
  console.error('❌ Lỗi khi đọc file tỉnh thành:', e.message);
}

const urlList = Array.from(urls);

console.log(`🔍 Tìm thấy tổng cộng ${urlList.length} URLs hợp lệ để gửi IndexNow.`);

async function pingIndexNow() {
  if (urlList.length === 0) {
    console.log('⚠️ Không tìm thấy URL nào để ping.');
    return;
  }

  console.log(`📤 Bắt đầu gửi ${urlList.length} URLs tới api.indexnow.org...`);

  try {
    const response = await fetch(`https://api.indexnow.org/indexnow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        host: host,
        key: key,
        keyLocation: keyLocation,
        urlList: urlList
      }),
    });

    if (response.status === 200 || response.status === 202) {
      console.log('✅ Đã gửi IndexNow thành công! Các công cụ tìm kiếm (Bing, Yandex, Seznam,...) đã nhận yêu cầu index nhanh.');
    } else {
      console.error('❌ Lỗi phản hồi từ IndexNow:', response.status, await response.text());
    }
  } catch (error) {
    console.error('❌ Lỗi kết nối IndexNow:', error.message);
  }
}

pingIndexNow();
