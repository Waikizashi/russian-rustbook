fn read_values(data: &[u8]) -> Option<Vec<u16>> {
    if data.len() % 2 != 0 {
        return None;
    }
    Some(
        data.chunks_exact(2)
            .map(|p| u16::from_be_bytes([p[0], p[1]]))
            .collect(),
    )
}

fn main() {
    assert_eq!(read_values(&[0, 1, 1, 0]), Some(vec![1, 256]));
    assert_eq!(read_values(&[]), Some(vec![]));
    assert_eq!(read_values(&[0]), None);
}
