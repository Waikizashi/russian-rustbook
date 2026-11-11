fn main() {
    let x = 0b0010_1000u8;
    assert_eq!(x.count_ones(), 2);
    assert_eq!(x.trailing_zeros(), 3);
    assert_eq!(x.leading_zeros(), 2);
    assert_eq!(0u8.trailing_zeros(), 8);
    assert_eq!(0b1000_0001u8.rotate_left(1), 0b0000_0011);
    assert_eq!(0b0000_0001u8.reverse_bits(), 0b1000_0000);
}
