#[repr(C)]
struct Header {
    tag: u8,
    length: u32,
}

fn main() {
    use std::mem::{align_of, size_of};
    let header = Header { tag: 1, length: 3 };
    assert_eq!(header.tag, 1);
    assert_eq!(header.length, 3);
    println!("u32 alignment: {}", align_of::<u32>());
    println!("Header size: {}", size_of::<Header>());
}
