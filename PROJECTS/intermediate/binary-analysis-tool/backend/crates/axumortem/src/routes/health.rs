// ©AngelaMos | 2026
// health.rs

use axum::extract::State;
use axum::Json;
use serde::Serialize;

use crate::state::AppState;

#[derive(Serialize)]
pub(crate) struct HealthResponse {
    status: &'static str,
    database: &'static str,
}

pub async fn check(
    State(state): State<AppState>,
) -> Json<HealthResponse> {
    let db_status =
        match sqlx::query("SELECT 1").execute(&state.db).await
        {
            Ok(_) => "connected",
            Err(_) => "disconnected",
        };

    Json(HealthResponse {
        status: "ok",
        database: db_status,
    })
}
