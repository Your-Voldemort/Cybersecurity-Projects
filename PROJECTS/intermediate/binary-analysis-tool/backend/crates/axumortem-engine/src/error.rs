// ©AngelaMos | 2026
// error.rs

#[derive(thiserror::Error, Debug)]
pub enum EngineError {
    #[error("invalid binary: {reason}")]
    InvalidBinary { reason: String },

    #[error("unsupported format: {format}")]
    UnsupportedFormat { format: String },

    #[error("unsupported architecture: {arch}")]
    UnsupportedArchitecture { arch: String },

    #[error("pass '{pass}' missing dependency: {dependency}")]
    MissingDependency {
        pass: String,
        dependency: String,
    },

    #[error("pass '{pass}' failed")]
    PassFailed {
        pass: &'static str,
        #[source]
        source: Box<dyn std::error::Error + Send + Sync>,
    },

    #[error("yara error: {0}")]
    Yara(String),

    #[error(transparent)]
    Io(#[from] std::io::Error),
}
