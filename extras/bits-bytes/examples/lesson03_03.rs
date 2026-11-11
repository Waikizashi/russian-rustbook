fn pack(version: u8, kind: u8) -> Option<u8> {
    if version > 7 || kind > 31 {
        return None;
    }
    Some((version << 5) | kind)
}

fn main() {
    let header = pack(5, 17).unwrap();
    assert_eq!(header, 0b1011_0001);
    assert_eq!(header >> 5, 5);
    assert_eq!(header & 0b1_1111, 17);
    assert_eq!(pack(8, 0), None);
    assert_eq!(pack(1, 32), None);
}
