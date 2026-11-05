use scraper::{Html, Selector};
use std::{
    io::{self, Write},
    time::Duration,
};
use tokio::time::{interval, timeout};

pub async fn fetch_dotarts(query: &str) -> Result<Vec<Box<str>>, String> {
    let request = async {
        reqwest::get(format!("https://emojicombos.com/{query}"))
            .await?
            .error_for_status()?
            .text()
            .await
    };

    tokio::pin!(request);
    let mut ticker = interval(Duration::from_millis(300));
    let mut n = 0u8;

    let inner = timeout(Duration::from_secs(5), async {
        loop {
            tokio::select! {
                result = &mut request => return result.map_err(|e| format!("Request error *-* ({e})")),
                _ = ticker.tick() => {
                    n = n % 3 + 1;
                    print!("\r\x1b[KSearching dotarts{}", ".".repeat(n as usize));
                    io::stdout().flush().ok();
                }
            }
        }
    })
    .await;

    print!("\r\x1b[K");
    io::stdout().flush().ok();

    let content = inner.map_err(|_| "Timeout error *-*".to_string())??;
    let document = Html::parse_document(&content);
    let selector = Selector::parse("div.emojis").unwrap();
    Ok(document
        .select(&selector)
        .filter_map(|el| {
            let text = el.text().next()?;
            let mut braille = 0;
            let mut blocks = 0;
            for c in text.chars() {
                match c {
                    '\u{2800}'..'\u{2900}' => braille += 1,
                    '\u{2580}'..'\u{25B0}' => blocks += 1,
                    _ => {}
                }
            }
            if blocks < 25 && braille < 25 {
                None
            } else {
                Some(Box::from(text))
            }
        })
        .collect())
}
