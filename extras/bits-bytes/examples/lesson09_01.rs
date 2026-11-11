use std::io::{self, Read, Write};

const MAX_FRAME: usize = 64 * 1024;

fn read_frame<R: Read>(reader: &mut R) -> io::Result<Vec<u8>> {
    let mut header = [0u8; 4];
    reader.read_exact(&mut header)?;
    let len = usize::try_from(u32::from_be_bytes(header))
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "length"))?;
    if len > MAX_FRAME {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "too large"));
    }
    let mut payload = vec![0u8; len];
    reader.read_exact(&mut payload)?;
    Ok(payload)
}

fn write_frame<W: Write>(writer: &mut W, payload: &[u8]) -> io::Result<()> {
    if payload.len() > MAX_FRAME {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "too large"));
    }
    let len = u32::try_from(payload.len())
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "length"))?;
    writer.write_all(&len.to_be_bytes())?;
    writer.write_all(payload)
}

fn main() -> io::Result<()> {
    let mut wire = Vec::new();
    write_frame(&mut wire, b"ABC")?;
    write_frame(&mut wire, "Ж".as_bytes())?;
    assert_eq!(&wire[..4], &[0, 0, 0, 3]);

    let mut reader = &wire[..];
    assert_eq!(read_frame(&mut reader)?, b"ABC");
    assert_eq!(read_frame(&mut reader)?, "Ж".as_bytes());
    assert!(reader.is_empty());
    assert!(read_frame(&mut reader).is_err());
    Ok(())
}
