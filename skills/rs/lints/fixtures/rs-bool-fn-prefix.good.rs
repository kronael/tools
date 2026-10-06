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

#[cfg(test)]
mod checks {
    fn valid_fixture() -> bool {
        true
    }
}
