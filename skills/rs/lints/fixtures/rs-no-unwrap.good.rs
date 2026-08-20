fn run(x: Option<i32>) -> i32 {
    x.expect("x is set at startup")
}
