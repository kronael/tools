fn run(x: Option<i32>) -> i32 {
    // config validated at startup; never None here
    x.unwrap()
}

fn safe(y: Option<i32>) -> i32 {
    y.expect("y is set at startup")
}
