fn main() {
    let valid = [0xD0, 0x96];
    assert_eq!(std::str::from_utf8(&valid).unwrap(), "Ж");

    let invalid = vec![0xFF];
    assert!(std::str::from_utf8(&invalid).is_err());
    assert_eq!(String::from_utf8_lossy(&invalid), "\u{FFFD}");
}
