import fs from 'fs';
import * as cheerio from 'cheerio';

const xmlFile = 'Báo cáo từ khóa phủ định.xml';

if (!fs.existsSync(xmlFile)) {
    console.error(`File không tồn tại: ${xmlFile}`);
    process.exit(1);
}

console.log(`Đang đọc file ${xmlFile}...`);
const xmlContent = fs.readFileSync(xmlFile, 'utf-8');
const $ = cheerio.load(xmlContent, { xmlMode: true });

const rows = [];
const uniqueKeys = new Set();
const duplicateRows = [];

$('row').each((i, row) => {
    let keyword = '';
    let matchType = '';
    let campaign = '';
    let adGroup = '';
    let level = '';
    let source = '';

    $(row).find('cell').each((j, cell) => {
        const key = $(cell).find('key').text().trim();
        const value = $(cell).find('value').text().trim();

        if (key === 'Từ khóa phủ định') {
            keyword = value;
        } else if (key === 'Loại đối sánh') {
            matchType = value;
        } else if (key === 'Chiến dịch') {
            campaign = value;
        } else if (key === 'Nhóm quảng cáo') {
            adGroup = value;
        } else if (key === 'Cấp độ') {
            level = value;
        } else if (key === 'Từ khóa hoặc danh sách') {
            source = value;
        }
    });

    // Chuẩn hóa và làm sạch từ khóa
    let CleanedKeyword = keyword
        .replace(/^""+/, '"') // Sửa lỗi dư hai dấu nháy đôi ở đầu
        .replace(/""+$/, '"') // Sửa lỗi dư hai dấu nháy đôi ở cuối
        .replace(/^"+|"+$/g, '') // Bỏ nháy đôi bao ngoài để chuẩn hóa
        .replace(/^\[+|\]+$/g, '') // Bỏ dấu ngoặc vuông bao ngoài để chuẩn hóa
        .trim();

    // Định dạng lại theo đúng định dạng Google Ads
    let formatted = '';
    if (matchType === 'Khớp chính xác' || keyword.startsWith('[')) {
        formatted = `[${CleanedKeyword}]`;
    } else if (matchType === 'Khớp cụm từ' || keyword.startsWith('"')) {
        formatted = `"${CleanedKeyword}"`;
    } else {
        formatted = CleanedKeyword;
    }

    // Tạo khóa duy nhất không phân biệt hoa thường
    const uniqueKey = formatted.toLowerCase();

    if (uniqueKeys.has(uniqueKey)) {
        duplicateRows.push({ original: keyword, formatted, matchType, campaign });
    } else {
        uniqueKeys.add(uniqueKey);
        rows.push({
            original: keyword,
            CleanedKeyword,
            formatted,
            matchType,
            campaign,
            adGroup,
            level,
            source
        });
    }
});

console.log(`\n--- KẾT QUẢ PHÂN TÍCH ---`);
console.log(`Tổng số dòng đã quét: ${$('row').length}`);
console.log(`Số từ khóa trùng lặp bị loại bỏ: ${duplicateRows.length}`);
console.log(`Số từ khóa độc nhất (đã lọc trùng): ${uniqueKeys.size}`);

// Xuất file text danh sách từ khóa độc nhất để sử dụng nhanh
const uniqueListText = Array.from(uniqueKeys).sort().join('\n');
fs.writeFileSync('tu_khoa_phu_dinh_unique.txt', uniqueListText, 'utf-8');
console.log(`=> Đã tạo file text: tu_khoa_phu_dinh_unique.txt`);

// Xuất file XML sạch nâng cấp lại để import vào Google Ads Editor
let outXml = `<?xml version='1.0' encoding='UTF-8'?>\n<report>\n\t<report-name>Báo cáo từ khóa phủ định đã lọc trùng</report-name>\n\t<date-range>Tất cả thời gian</date-range>\n\t<table>\n`;

rows.forEach(r => {
    outXml += `\t\t<row>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Từ khóa phủ định</key>\n\t\t\t\t<value>${escapeXml(r.formatted)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Từ khóa hoặc danh sách</key>\n\t\t\t\t<value>${escapeXml(r.source)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Chiến dịch</key>\n\t\t\t\t<value>${escapeXml(r.campaign)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Nhóm quảng cáo</key>\n\t\t\t\t<value>${escapeXml(r.adGroup)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Cấp độ</key>\n\t\t\t\t<value>${escapeXml(r.level)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t\t<cell>\n\t\t\t\t<key>Loại đối sánh</key>\n\t\t\t\t<value>${escapeXml(r.matchType)}</value>\n\t\t\t</cell>\n`;
    outXml += `\t\t</row>\n`;
});

outXml += `\t</table>\n</report>`;
fs.writeFileSync('Báo cáo từ khóa phủ định_clean.xml', outXml, 'utf-8');
console.log(`=> Đã tạo file XML sạch: Báo cáo từ khóa phủ định_clean.xml`);

function escapeXml(unsafe) {
    return unsafe.replace(/[<>&'"]/g, function (c) {
        switch (c) {
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '&': return '&amp;';
            case '\'': return '&apos;';
            case '"': return '&quot;';
        }
    });
}
