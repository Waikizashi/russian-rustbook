fn main() {
    let x = 250u8;
    assert_eq!(x.checked_add(10), None);
    assert_eq!(x.wrapping_add(10), 4);
    assert_eq!(x.saturating_add(10), 255);
    assert_eq!(x.overflowing_add(10), (4, true));
}
