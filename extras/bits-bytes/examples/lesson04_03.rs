fn main() {
    let x = 1.0f32;
    assert_eq!(x.to_bits(), 0x3F80_0000);
    assert_eq!(x.to_bits().to_be_bytes(), [0x3F, 0x80, 0, 0]);
    assert_eq!(f32::from_bits(0x3F80_0000), 1.0);
    assert_eq!(1.5f32 as u32, 1);
    assert_ne!(1.5f32.to_bits(), 1);
}
