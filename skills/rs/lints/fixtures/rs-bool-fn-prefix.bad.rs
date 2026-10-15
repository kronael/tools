fn valid(slot: u64) -> bool {
    slot > 0
}

async fn alive() -> bool {
    true
}

#[cfg(not(test))]
fn prod_only() -> bool {
    true
}

#[cfg_attr(test, allow(dead_code))]
fn spare() -> bool {
    true
}

#[allow(clippy::contest)]
fn contest() -> bool {
    true
}

#[doc = "attestation"]
fn attested() -> bool {
    true
}

#[cfg(not(test))]
mod prod {
    fn ready() -> bool {
        true
    }
}

#[cfg(any(test, feature = "verify"))]
mod verify {
    fn signed() -> bool {
        true
    }
}

mod tests_util {
    fn ready() -> bool {
        true
    }
}

#[test]
fn checks_slot() {}
fn after_test() -> bool {
    true
}
