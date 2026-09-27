fn parse(v: &Value) -> Foo {
    serde_json::from_value::<Foo>(v.clone()).unwrap_or_default()
}
