fn read_u16_at(data: &[u8], offset: usize) -> Option<u16> {
    let end = offset.checked_add(2)?;
    let part = data.get(offset..end)?;
    Some(u16::from_be_bytes([part[0], part[1]]))
}

fn main() {
    let data = [0xAA, 0x01, 0x02];
    assert_eq!(read_u16_at(&data, 1), Some(258));
    assert_eq!(read_u16_at(&data, 2), None);
    assert_eq!(read_u16_at(&data, usize::MAX), None);
}
