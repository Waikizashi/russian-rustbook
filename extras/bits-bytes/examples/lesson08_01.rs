#[derive(Debug, PartialEq, Eq)]
enum VarintError {
    Truncated,
    Overflow,
    NonCanonical,
}

fn encode(mut n: u64) -> Vec<u8> {
    let mut out = Vec::new();
    loop {
        let mut byte = (n & 0x7F) as u8;
        n >>= 7;
        if n != 0 {
            byte |= 0x80;
        }
        out.push(byte);
        if n == 0 {
            return out;
        }
    }
}

fn decode(data: &[u8]) -> Result<(u64, usize), VarintError> {
    let mut value = 0u64;
    for i in 0..10usize {
        let byte = *data.get(i).ok_or(VarintError::Truncated)?;
        if i == 9 && byte > 1 {
            return Err(VarintError::Overflow);
        }
        let group = byte & 0x7F;
        value |= u64::from(group) << (7 * i);
        if byte & 0x80 == 0 {
            if i > 0 && group == 0 {
                return Err(VarintError::NonCanonical);
            }
            return Ok((value, i + 1));
        }
    }
    Err(VarintError::Overflow)
}

fn main() {
    assert_eq!(encode(300), [0xAC, 0x02]);
    assert_eq!(decode(&[0xAC, 0x02, 0x99]), Ok((300, 2)));
    for n in [0, 1, 127, 128, 300, u64::MAX] {
        let bytes = encode(n);
        assert_eq!(decode(&bytes), Ok((n, bytes.len())));
    }
    assert_eq!(decode(&[0x80]), Err(VarintError::Truncated));
    assert_eq!(decode(&[0x80, 0]), Err(VarintError::NonCanonical));
    assert_eq!(decode(&[0xFF; 10]), Err(VarintError::Overflow));
}
