fn main() {
    const READ: u8 = 1 << 0;
    const WRITE: u8 = 1 << 1;
    const EXECUTE: u8 = 1 << 2;
    const KNOWN: u8 = READ | WRITE | EXECUTE;

    let mut flags = READ | WRITE;
    assert!(flags & READ != 0);
    assert!(flags & EXECUTE == 0);

    flags |= EXECUTE;
    flags &= !WRITE;
    flags ^= READ;
    assert_eq!(flags, EXECUTE);
    assert_eq!(flags & !KNOWN, 0);
}
