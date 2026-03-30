// ©AngelaMos | 2026
// state.rs

use std::sync::Arc;

use axumortem_engine::AnalysisEngine;
use sqlx::PgPool;

use crate::config::AppConfig;

#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
    pub engine: Arc<AnalysisEngine>,
    pub config: Arc<AppConfig>,
}
