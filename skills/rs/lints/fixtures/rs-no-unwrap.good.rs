fn run(x: Option<i32>) -> i32 {
    // ast-grep-ignore: rs-no-unwrap
    x.unwrap()
}

fn safe(y: Option<i32>) -> i32 {
    y.expect("y is set at startup")
}
