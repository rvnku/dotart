use crate::{
    args::{Args, Target},
    request::fetch_dotarts,
    utils::{img2braille, reverse_braille},
};
use clap::Parser;
use image::ImageReader;
use rand::random_range;
use std::{error::Error, num::NonZeroU16};
mod args;
mod request;
mod utils;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();
    match args.target {
        Target::Query(query) => println!(
            "{}",
            match fetch_dotarts(query.as_str()).await {
                Ok(dotarts) => {
                    if dotarts.is_empty() {
                        "No arts found -_-".to_string()
                    } else {
                        let count = dotarts.len();
                        let index = args.index.unwrap_or(unsafe {
                            NonZeroU16::new_unchecked(random_range(1..=count as u16))
                        });
                        if let Some(dotart) = dotarts.into_iter().nth((index.get() - 1) as usize) {
                            let dotart = if args.reverse {
                                reverse_braille(&dotart).into_boxed_str()
                            } else {
                                dotart
                            };
                            format!("{}\nArt: {} / {}", dotart, index, count)
                        } else {
                            "Art not exists *-*".to_string()
                        }
                    }
                }
                Err(error) => error,
            }
        ),
        Target::Path(path) => {
            let size = termsize::get().unwrap();
            let image = ImageReader::open(path)?.decode()?;
            print!(
                "{}",
                img2braille(
                    &image,
                    size.cols,
                    size.rows,
                    args.px,
                    args.threshold,
                    args.reverse
                )
            )
        }
    }
    Ok(())
}
