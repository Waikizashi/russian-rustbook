fn main() {
    assert_eq!(0b0000_1101u8 << 2, 0b0011_0100);
    assert_eq!(0b0000_1101u8 >> 2, 0b0000_0011);
    assert_eq!(0b1000_0001u8 << 1, 0b0000_0010);

    assert_eq!(1u8.checked_shl(7), Some(128));
    assert_eq!(1u8.checked_shl(8), None);
    assert_eq!(128u8.checked_shl(1), Some(0));

    assert_eq!(-3i8 >> 1, -2);
    assert_eq!(-3i8 / 2, -1);
}
