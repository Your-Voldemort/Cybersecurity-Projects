// ©AngelaMos | 2026
// config.rs

use clap::Parser;

const DEFAULT_HOST: &str = "0.0.0.0";
const DEFAULT_PORT: u16 = 3000;
const DEFAULT_MAX_UPLOAD_BYTES: usize = 52_428_800;
const DEFAULT_CORS_ORIGIN: &str = "*";

#[derive(Parser, Debug)]
pub struct AppConfig {
    #[arg(long, env = "DATABASE_URL")]
    pub database_url: String,

    #[arg(long, env = "HOST", default_value = DEFAULT_HOST)]
    pub host: String,

    #[arg(long, env = "PORT", default_value_t = DEFAULT_PORT)]
    pub port: u16,

    #[arg(long, env = "MAX_UPLOAD_SIZE", default_value_t = DEFAULT_MAX_UPLOAD_BYTES)]
    pub max_upload_size: usize,

    #[arg(long, env = "CORS_ORIGIN", default_value = DEFAULT_CORS_ORIGIN)]
    pub cors_origin: String,
}

impl AppConfig {
    pub fn bind_address(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}
