// ©AngelaMos | 2026
// cors.rs

use axum::http::header::{HeaderName, ACCEPT, CONTENT_TYPE};
use axum::http::Method;
use tower_http::cors::{Any, CorsLayer};

use crate::config::AppConfig;

const ALLOWED_METHODS: [Method; 3] =
    [Method::GET, Method::POST, Method::OPTIONS];

const ALLOWED_HEADERS: [HeaderName; 2] =
    [CONTENT_TYPE, ACCEPT];

pub fn layer(config: &AppConfig) -> CorsLayer {
    let base = CorsLayer::new()
        .allow_methods(ALLOWED_METHODS)
        .allow_headers(ALLOWED_HEADERS);

    if config.cors_origin == "*" {
        base.allow_origin(Any)
    } else {
        base.allow_origin([config
            .cors_origin
            .parse()
            .expect("invalid CORS origin header value")])
    }
}
