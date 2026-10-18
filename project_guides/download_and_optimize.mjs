import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const rawDir = 'c:/Users/hp/Desktop/fptwebsite/app/picturecbvvip';
const destDir = 'c:/Users/hp/Desktop/fptwebsite/public/images/optimized';

if (!fs.existsSync(rawDir)) {
    fs.mkdirSync(rawDir, { recursive: true });
}

if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
}

const imagesToProcess = [
    {
        url: 'https://hi-static.fpt.vn/sys/shop/prod/2026-09-09/6aa12d2302d3a_Combo%20giga%20vvip.jpg',
        rawName: 'combo-giga-vvip.jpg',
        dest: 'giga-vvip.webp'
    },
    {
        url: 'https://hi-static.fpt.vn/sys/shop/prod/2026-09-09/6aa1308c5eda6_Combo%20sky%20vvip.jpg',
        rawName: 'combo-sky-vvip.jpg',
        dest: 'sky-vvip.webp'
    },
    {
        url: 'https://hi-static.fpt.vn/sys/shop/prod/2026-09-09/6aa130aa6f0ed_Combo%20meta%20vvip.jpg',
        rawName: 'combo-meta-vvip.jpg',
        dest: 'meta-vvip.webp'
    },
    {
        url: 'https://hi-static.fpt.vn/sys/shop/prod/2026-09-09/6aa1314448764_COMBO%20LUX500%20-%20VVIP.jpg',
        rawName: 'combo-lux500-vvip.jpg',
        dest: 'lux500-vvip.webp'
    },
    {
        url: 'https://hi-static.fpt.vn/sys/shop/prod/2026-09-09/6aa13162a6155_COMBO%20LUX800%20-%20VVIP.jpg',
        rawName: 'combo-lux800-vvip.jpg',
        dest: 'lux800-vvip.webp'
    }
];

async function run() {
    for (const item of imagesToProcess) {
        const rawPath = path.join(rawDir, item.rawName);
        const destPath = path.join(destDir, item.dest);
        console.log(`Downloading ${item.url} ...`);
        try {
            const res = await fetch(item.url);
            if (!res.ok) {
                throw new Error(`Failed to fetch: ${res.statusText}`);
            }
            const buffer = Buffer.from(await res.arrayBuffer());
            // Save raw downloaded image to local with clean name
            fs.writeFileSync(rawPath, buffer);
            console.log(`Saved raw image to ${item.rawName}`);

            // Optimize to webp with quality 85
            console.log(`Optimizing to ${item.dest}...`);
            await sharp(buffer)
                .webp({ quality: 85 })
                .toFile(destPath);
            console.log(`Successfully created ${item.dest}`);
        } catch (err) {
            console.error(`Error processing ${item.dest}:`, err);
        }
    }
}

run();
