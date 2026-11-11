#[derive(Debug, PartialEq, Eq)]
enum ParseError {
    Truncated,
    Version,
    Flags,
    TrailingBytes,
}

fn parse(data: &[u8]) -> Result<(u8, &[u8]), ParseError> {
    let header = data.get(..4).ok_or(ParseError::Truncated)?;
    if header[0] != 1 {
        return Err(ParseError::Version);
    }
    let flags = header[1];
    if flags & !0b11 != 0 {
        return Err(ParseError::Flags);
    }
    let len = usize::from(u16::from_be_bytes([header[2], header[3]]));
    let payload = data.get(4..).ok_or(ParseError::Truncated)?;
    if payload.len() < len {
        return Err(ParseError::Truncated);
    }
    if payload.len() > len {
        return Err(ParseError::TrailingBytes);
    }
    Ok((flags, payload))
}

fn main() {
    let packet = [1, 0b01, 0, 3, 10, 20, 30];
    assert_eq!(parse(&packet), Ok((1, &[10, 20, 30][..])));
    assert_eq!(parse(&packet[..6]), Err(ParseError::Truncated));
    assert_eq!(parse(&[2, 0, 0, 0]), Err(ParseError::Version));
    assert_eq!(parse(&[1, 4, 0, 0]), Err(ParseError::Flags));
    assert_eq!(parse(&[1, 0, 0, 0, 9]), Err(ParseError::TrailingBytes));
}
