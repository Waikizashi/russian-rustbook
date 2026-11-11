fn main() {
    let s = "AЖ🦀";
    assert_eq!(s.get(1..3), Some("Ж"));
    assert_eq!(s.get(1..2), None);
    assert_eq!(&s.as_bytes()[1..2], &[0xD0]);

    let decomposed = "e\u{301}";
    assert_eq!(decomposed.chars().count(), 2);
    assert_eq!(decomposed.len(), 3);
}
