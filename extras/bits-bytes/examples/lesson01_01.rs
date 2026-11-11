fn main() {
    let n: u8 = 45;
    assert_eq!(n, 0b0010_1101);
    assert_eq!(n, 0x2D);
    assert_eq!(format!("{n:08b}"), "00101101");
    assert_eq!(format!("{n:02X}"), "2D");
    println!("decimal={n}, binary={n:08b}, hex={n:02X}");
}
