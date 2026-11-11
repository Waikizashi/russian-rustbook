fn main() {
    let (r, g, b, a) = (0x12u8, 0x34u8, 0x56u8, 0xFFu8);
    let color = (u32::from(r) << 24) | (u32::from(g) << 16) | (u32::from(b) << 8) | u32::from(a);
    assert_eq!(color, 0x1234_56FF);
    assert_eq!(((color >> 16) & 0xFF) as u8, g);
    assert_eq!(color.to_be_bytes(), [r, g, b, a]);
}
