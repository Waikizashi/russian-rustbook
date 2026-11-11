fn main() {
    let data = b"Rust\x00\xFF";
    for (row, chunk) in data.chunks(8).enumerate() {
        print!("{:04X}: ", row * 8);
        for byte in chunk {
            print!("{byte:02X} ");
        }
        println!();
    }
}
