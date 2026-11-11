fn main() {
    let wire_length = 1024u32;
    let length = usize::try_from(wire_length).unwrap();
    const MAX_PAYLOAD: usize = 64 * 1024;
    assert!(length <= MAX_PAYLOAD);
    assert_eq!(wire_length.to_be_bytes(), [0, 0, 4, 0]);
}
