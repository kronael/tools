fn parse(v: &Value) -> Foo {
    Foo::deserialize(v).unwrap_or_default()
}
