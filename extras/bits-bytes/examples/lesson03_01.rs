fn main() {
    let a = 0b1010u8;
    let b = 0b1100u8;
    assert_eq!(a & b, 0b1000);
    assert_eq!(a | b, 0b1110);
    assert_eq!(a ^ b, 0b0110);
    assert_eq!(!a, 0b1111_0101);
}
