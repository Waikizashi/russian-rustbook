fn main() {
    let bits = 0xFFu8;
    assert_eq!(bits, 255);
    assert_eq!(bits as i8, -1);
    assert_eq!((-5i8) as u8, 0b1111_1011);
    assert_eq!(i8::MIN, -128);
    assert_eq!(i8::MAX, 127);
}
