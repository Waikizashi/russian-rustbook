fn main() {
    let mut bytes = Vec::with_capacity(8);
    assert_eq!(bytes.len(), 0);
    assert!(bytes.capacity() >= 8);
    bytes.extend_from_slice(&[0xAB, 0xCD]);
    bytes.push(0xEF);
    assert_eq!(bytes.as_slice(), &[0xAB, 0xCD, 0xEF]);

    let header: &[u8] = &bytes[..2];
    assert_eq!(header, &[0xAB, 0xCD]);

    let initialized = vec![0u8; 8];
    assert_eq!(initialized.len(), 8);
}
