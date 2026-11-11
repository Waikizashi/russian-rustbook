use byte_note::{Error, MAX_PAYLOAD, URGENT, UTF8, crc32, decode, encode};

const GOLDEN: &[u8] = &[
    0x42, 0x59, 0x54, 0x45, 0x21, 0x01, 0x00, 0x03, 0x04, 0x03, 0x02, 0x01, 0x41, 0xD0, 0x96, 0x22,
    0xF4, 0x2A, 0x3A,
];

fn refresh_crc(bytes: &mut [u8]) {
    let end = bytes.len() - 4;
    let checksum = crc32(&bytes[..end]);
    bytes[end..].copy_from_slice(&checksum.to_be_bytes());
}

#[test]
fn known_crc_vector() {
    assert_eq!(crc32(b"123456789"), 0xCBF4_3926);
    assert_eq!(crc32(b""), 0);
}

#[test]
fn exact_golden_bytes() {
    let encoded = encode(1, UTF8, 0x0102_0304, "AЖ".as_bytes()).unwrap();
    assert_eq!(encoded, GOLDEN);
    let message = decode(GOLDEN).unwrap();
    assert_eq!(message.kind, 1);
    assert_eq!(message.flags, UTF8);
    assert_eq!(message.sequence, 0x0102_0304);
    assert_eq!(message.text(), Ok(Some("AЖ")));
}

#[test]
fn empty_and_maximum_payloads() {
    for length in [0, 1, MAX_PAYLOAD] {
        let payload = vec![0xFF; length];
        let bytes = encode(31, URGENT, u32::MAX, &payload).unwrap();
        let message = decode(&bytes).unwrap();
        assert_eq!(message.payload, payload);
        assert_eq!(message.text(), Ok(None));
        assert_eq!(message.sequence, u32::MAX);
        assert_eq!(bytes.len(), 16 + length);
    }
    let bytes = encode(0, UTF8, 0, b"").unwrap();
    assert_eq!(decode(&bytes).unwrap().text(), Ok(Some("")));
}

#[test]
fn every_truncation_is_an_error() {
    for end in 0..GOLDEN.len() {
        assert_eq!(decode(&GOLDEN[..end]), Err(Error::Truncated));
    }
}

#[test]
fn every_single_bit_change_is_rejected() {
    for index in 0..GOLDEN.len() {
        for bit in 0..8 {
            let mut changed = GOLDEN.to_vec();
            changed[index] ^= 1 << bit;
            assert!(decode(&changed).is_err());
        }
    }
}

#[test]
fn encoder_rejects_invalid_fields() {
    assert_eq!(encode(32, 0, 0, b""), Err(Error::Kind));
    assert_eq!(encode(0, 4, 0, b""), Err(Error::Flags));
    assert_eq!(encode(0, UTF8, 0, &[0xFF]), Err(Error::Utf8));
    assert_eq!(
        encode(0, 0, 0, &vec![0; MAX_PAYLOAD + 1]),
        Err(Error::TooLarge)
    );
}

#[test]
fn decoder_checks_version_flags_and_magic() {
    let mut bytes = GOLDEN.to_vec();
    bytes[0] = 0;
    assert_eq!(decode(&bytes), Err(Error::Magic));
    bytes = GOLDEN.to_vec();
    bytes[4] = 0x41;
    assert_eq!(decode(&bytes), Err(Error::Version));
    bytes = GOLDEN.to_vec();
    bytes[5] = 4;
    assert_eq!(decode(&bytes), Err(Error::Flags));
}

#[test]
fn decoder_checks_lengths() {
    let mut bytes = GOLDEN.to_vec();
    bytes.push(0);
    assert_eq!(decode(&bytes), Err(Error::TrailingBytes));
    bytes = GOLDEN.to_vec();
    bytes[6..8].copy_from_slice(&4097u16.to_be_bytes());
    assert_eq!(decode(&bytes), Err(Error::TooLarge));
    bytes[6..8].copy_from_slice(&4u16.to_be_bytes());
    assert_eq!(decode(&bytes), Err(Error::Truncated));
    bytes[6..8].copy_from_slice(&2u16.to_be_bytes());
    assert_eq!(decode(&bytes), Err(Error::TrailingBytes));
}

#[test]
fn checksum_and_utf8_are_independent_checks() {
    let mut bytes = GOLDEN.to_vec();
    bytes[12] = b'B';
    assert_eq!(decode(&bytes), Err(Error::Checksum));
    bytes[12] = 0xFF;
    refresh_crc(&mut bytes);
    assert_eq!(decode(&bytes), Err(Error::Utf8));

    let binary = encode(1, 0, 7, &[0xFF, 0]).unwrap();
    assert_eq!(decode(&binary).unwrap().payload, &[0xFF, 0]);
}

#[test]
fn all_kinds_and_known_flag_combinations() {
    for kind in 0..=31 {
        for flags in 0..=3 {
            let bytes = encode(kind, flags, 7, b"hello").unwrap();
            let message = decode(&bytes).unwrap();
            assert_eq!((message.kind, message.flags), (kind, flags));
        }
    }
}
