fn main() {
    assert_eq!(u8::try_from(200u16), Ok(200));
    assert!(u8::try_from(300u16).is_err());
    assert_eq!(300u16 as u8, 44);
    assert!(u8::try_from(-1i32).is_err());
}
