struct Slot(u64);

impl Slot {
    fn is_valid(&self) -> bool {
        self.0 > 0
    }
}

impl PartialEq for Slot {
    fn eq(&self, other: &Slot) -> bool {
        self.0 == other.0
    }
}

fn count(slots: &[Slot]) -> usize {
    slots.len()
}

#[test]
fn valid_slot() -> bool {
    true
}

#[test]
#[ignore]
fn slow_slot() -> bool {
    true
}

#[test]
/// Slot zero is invalid.
fn zero_slot() -> bool {
    true
}

#[test] // returns bool to exercise the harness
fn bool_slot() -> bool {
    true
}

#[tokio::test(flavor = "multi_thread")]
async fn async_slot() -> bool {
    true
}

#[rstest]
fn case_slot() -> bool {
    true
}

#[test_case(1)]
fn one_slot() -> bool {
    true
}

#[test]
fn outer_slot() {
    fn inner_valid() -> bool {
        true
    }
    assert!(inner_valid());
}

#[cfg(test)]
fn fixture_valid() -> bool {
    true
}

#[cfg(test)]
mod checks {
    fn valid_fixture() -> bool {
        true
    }
}

#[cfg(test)]
// helpers shared by the checks
mod helpers {
    fn ready() -> bool {
        true
    }
}

#[cfg(all(test, feature = "slow"))]
mod slow {
    fn ready() -> bool {
        true
    }
}

#[cfg(test)]
impl Slot {
    fn fixture(&self) -> bool {
        true
    }
}

mod tests {
    fn ready() -> bool {
        true
    }
}

mod test {
    fn ready() -> bool {
        true
    }
}
