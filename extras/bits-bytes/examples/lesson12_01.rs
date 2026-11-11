fn contains(set: u64, index: u32) -> Option<bool> {
    let mask = 1u64.checked_shl(index)?;
    Some(set & mask != 0)
}

fn insert(set: u64, index: u32) -> Option<u64> {
    let mask = 1u64.checked_shl(index)?;
    Some(set | mask)
}

fn main() {
    let set = insert(0, 63).unwrap();
    assert_eq!(contains(set, 63), Some(true));
    assert_eq!(contains(set, 0), Some(false));
    assert_eq!(insert(set, 64), None);
    assert_eq!(set.count_ones(), 1);
}
