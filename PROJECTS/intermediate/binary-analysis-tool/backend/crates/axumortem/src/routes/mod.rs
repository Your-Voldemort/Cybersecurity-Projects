// ©AngelaMos | 2026
// mod.rs

mod analysis;
mod health;
mod upload;

use axum::routing::{get, post};
use axum::Router;

use crate::state::AppState;

pub fn api_router() -> Router<AppState> {
    Router::new()
        .route("/api/health", get(health::check))
        .route("/api/upload", post(upload::handle))
        .route(
            "/api/analysis/{slug}",
            get(analysis::get_by_slug),
        )
}
