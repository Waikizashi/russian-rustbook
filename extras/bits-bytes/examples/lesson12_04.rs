fn main() {
    let n = 0b1001_0000u8;
    assert_eq!(n << 2, 0b0100_0000);
    assert_eq!(n.rotate_left(2), 0b0100_0010);
}
