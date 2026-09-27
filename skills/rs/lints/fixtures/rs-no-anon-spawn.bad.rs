fn start(client: Client) {
    tokio::spawn(async move {
        fetch(client).await;
    });
}
