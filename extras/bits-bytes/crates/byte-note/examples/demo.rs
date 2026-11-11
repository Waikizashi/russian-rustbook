use byte_note::{UTF8, decode, encode};

fn main() {
    let bytes = encode(1, UTF8, 0x0102_0304, "AЖ".as_bytes()).unwrap();
    for b in &bytes {
        print!("{b:02X} ");
    }
    println!();
    let message = decode(&bytes).unwrap();
    println!("kind={}, sequence={:#010X}", message.kind, message.sequence);
    println!("text={}", message.text().unwrap().unwrap());
}
