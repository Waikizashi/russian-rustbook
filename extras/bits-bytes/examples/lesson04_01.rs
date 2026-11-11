fn main() {
    let n = 0x1234_5678u32;
    assert_eq!(n.to_be_bytes(), [0x12, 0x34, 0x56, 0x78]);
    assert_eq!(n.to_le_bytes(), [0x78, 0x56, 0x34, 0x12]);

    let bytes = [0x01, 0x02];
    assert_eq!(u16::from_be_bytes(bytes), 258);
    assert_eq!(u16::from_le_bytes(bytes), 513);
}
