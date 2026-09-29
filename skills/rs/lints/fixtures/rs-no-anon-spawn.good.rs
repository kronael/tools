async fn fetch_and_process(client: Client) {
    fetch(client).await;
}

fn start(client: Client) {
    tokio::spawn(fetch_and_process(client));
}
