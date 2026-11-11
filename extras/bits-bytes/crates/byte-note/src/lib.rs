// SECTION: types
pub const MAX_PAYLOAD: usize = 4096;
pub const UTF8: u8 = 1 << 0;
pub const URGENT: u8 = 1 << 1;
const KNOWN_FLAGS: u8 = UTF8 | URGENT;
const HEADER_LEN: usize = 12;
const CRC_LEN: usize = 4;

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    Truncated,
    Magic,
    Version,
    Kind,
    Flags,
    TooLarge,
    TrailingBytes,
    Checksum,
    Utf8,
}

#[derive(Debug, PartialEq, Eq)]
pub struct Message<'a> {
    pub kind: u8,
    pub flags: u8,
    pub sequence: u32,
    pub payload: &'a [u8],
}

impl<'a> Message<'a> {
    pub fn text(&self) -> Result<Option<&'a str>, Error> {
        if self.flags & UTF8 == 0 {
            return Ok(None);
        }
        std::str::from_utf8(self.payload)
            .map(Some)
            .map_err(|_| Error::Utf8)
    }
}
// END: types

// SECTION: crc
pub fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xFFFF_FFFFu32;
    for &byte in data {
        crc ^= u32::from(byte);
        for _ in 0..8 {
            crc = if crc & 1 != 0 {
                (crc >> 1) ^ 0xEDB8_8320
            } else {
                crc >> 1
            };
        }
    }
    !crc
}
// END: crc

// SECTION: encode
pub fn encode(kind: u8, flags: u8, sequence: u32, payload: &[u8]) -> Result<Vec<u8>, Error> {
    if kind > 31 {
        return Err(Error::Kind);
    }
    if flags & !KNOWN_FLAGS != 0 {
        return Err(Error::Flags);
    }
    if payload.len() > MAX_PAYLOAD {
        return Err(Error::TooLarge);
    }
    if flags & UTF8 != 0 {
        std::str::from_utf8(payload).map_err(|_| Error::Utf8)?;
    }
    let len = u16::try_from(payload.len()).map_err(|_| Error::TooLarge)?;
    let mut out = Vec::with_capacity(HEADER_LEN + payload.len() + CRC_LEN);
    out.extend_from_slice(b"BYTE");
    out.push((1 << 5) | kind);
    out.push(flags);
    out.extend_from_slice(&len.to_be_bytes());
    out.extend_from_slice(&sequence.to_le_bytes());
    out.extend_from_slice(payload);
    let checksum = crc32(&out);
    out.extend_from_slice(&checksum.to_be_bytes());
    Ok(out)
}
// END: encode

// SECTION: decode
pub fn decode(data: &[u8]) -> Result<Message<'_>, Error> {
    let header = data.get(..HEADER_LEN).ok_or(Error::Truncated)?;
    if &header[..4] != b"BYTE" {
        return Err(Error::Magic);
    }
    if header[4] >> 5 != 1 {
        return Err(Error::Version);
    }
    let kind = header[4] & 0x1F;
    let flags = header[5];
    if flags & !KNOWN_FLAGS != 0 {
        return Err(Error::Flags);
    }
    let len = usize::from(u16::from_be_bytes([header[6], header[7]]));
    if len > MAX_PAYLOAD {
        return Err(Error::TooLarge);
    }
    let crc_offset = HEADER_LEN.checked_add(len).ok_or(Error::TooLarge)?;
    let required = crc_offset.checked_add(CRC_LEN).ok_or(Error::TooLarge)?;
    if data.len() < required {
        return Err(Error::Truncated);
    }
    if data.len() > required {
        return Err(Error::TrailingBytes);
    }
    let sequence = u32::from_le_bytes([header[8], header[9], header[10], header[11]]);
    let checksum = u32::from_be_bytes([
        data[crc_offset],
        data[crc_offset + 1],
        data[crc_offset + 2],
        data[crc_offset + 3],
    ]);
    if crc32(&data[..crc_offset]) != checksum {
        return Err(Error::Checksum);
    }
    let payload = &data[HEADER_LEN..crc_offset];
    if flags & UTF8 != 0 {
        std::str::from_utf8(payload).map_err(|_| Error::Utf8)?;
    }
    Ok(Message {
        kind,
        flags,
        sequence,
        payload,
    })
}
// END: decode
