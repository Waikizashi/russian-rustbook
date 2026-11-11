fn main() {
    assert_eq!(b'A', 65);
    assert_eq!(b'0', 48);
    assert_eq!("Ж".as_bytes(), &[0xD0, 0x96]);
    assert_eq!("🦀".as_bytes(), &[0xF0, 0x9F, 0xA6, 0x80]);

    let s = "AЖ🦀";
    assert_eq!(s.len(), 7);
    assert_eq!(s.chars().count(), 3);
    assert_eq!(std::mem::size_of::<char>(), 4);
}
