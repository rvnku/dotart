use image::{DynamicImage, GenericImageView, ImageBuffer, Luma, imageops::FilterType};

const BRAILLE_BITS: [(u16, u16, u16); 8] = [
    (0, 0, 0x01),
    (0, 1, 0x02),
    (0, 2, 0x04),
    (0, 3, 0x40),
    (1, 0, 0x08),
    (1, 1, 0x10),
    (1, 2, 0x20),
    (1, 3, 0x80),
];

fn pixel2braille(
    buffer: &ImageBuffer<Luma<u8>, Vec<u8>>,
    x: u16,
    y: u16,
    w: u16,
    h: u16,
    threshold: u8,
    reverse: bool,
) -> char {
    let mut bytes: u16 = 0x2800;
    for (dx, dy, bit) in BRAILLE_BITS {
        if x + dx >= w || y + dy >= h {
            continue;
        }
        let val = buffer.get_pixel((x + dx) as u32, (y + dy) as u32).0[0];
        if (val > threshold) != reverse {
            bytes |= bit;
        }
    }
    unsafe { char::from_u32_unchecked(bytes as u32) }
}

pub fn img2braille(
    image: &DynamicImage,
    cols: u16,
    rows: u16,
    px: Option<u16>,
    threshold: u8,
    reverse: bool,
) -> String {
    let (width, height) = image.dimensions();
    let (c, r) = (cols * 2, (rows - 2) * 4);
    let ratio = width as f32 / height as f32;
    let (w, h) = {
        let (fw, fh) = if ratio < c as f32 / r as f32 {
            (ratio * r as f32, r as f32)
        } else {
            (c as f32, c as f32 / ratio)
        };
        if let Some(px) = px {
            let s = (px as f32 / fw.min(fh)).min(1.);
            ((fw * s) as u16, (fh * s) as u16)
        } else {
            (fw as u16, fh as u16)
        }
    };
    let (ceils, lines) = (w.div_ceil(2), h.div_ceil(4));
    let buffer = image
        .resize_exact(w as u32, h as u32, FilterType::Nearest)
        .into_luma8();

    let mut dotart = String::with_capacity((lines * (ceils * 3 + 1)) as usize);
    for y in (0..h).step_by(4) {
        for x in (0..w).step_by(2) {
            dotart.push(pixel2braille(&buffer, x, y, w, h, threshold, reverse));
        }
        dotart.push('\n');
    }
    dotart
}

pub fn reverse_braille(string: &Box<str>) -> String {
    let mut result = String::with_capacity(string.len());
    for c in string.chars() {
        result.push(match c {
            '\u{2800}'..'\u{2900}' => unsafe { char::from_u32_unchecked((c as u32) ^ 0xFF) },
            c => c,
        });
    }
    result
}
