use clap::Parser;
use std::{
    num::NonZeroU16,
    path::{Component, Path, PathBuf},
    str::FromStr,
};

#[derive(Parser, Debug)]
#[command()]
pub struct Args {
    /// Path to image or query for search
    #[arg(required = true)]
    pub target: Target,

    /// Replace dots and spaces in the image
    #[arg(long)]
    pub reverse: bool,

    /// Image size along the short side (only for custom images)
    #[arg(long)]
    pub px: Option<u16>,

    /// Brightness threshold for the image (only for custom images)
    #[arg(long, default_value_t = 0x80)]
    pub threshold: u8,

    /// The number of the dotart (only for searched images)
    #[arg(long)]
    pub index: Option<NonZeroU16>,
}

#[derive(Debug, Clone)]
pub enum Target {
    Path(PathBuf),
    Query(String),
}

impl FromStr for Target {
    type Err = std::convert::Infallible;

    fn from_str(argument: &str) -> Result<Self, Self::Err> {
        let path = Path::new(argument);
        if path.is_absolute()
            || path.has_root()
            || matches!(
                path.components().next(),
                Some(Component::CurDir) | Some(Component::RootDir) | Some(Component::Prefix(_))
            )
        {
            Ok(Target::Path(PathBuf::from(path)))
        } else {
            Ok(Target::Query(argument.to_string()))
        }
    }
}
