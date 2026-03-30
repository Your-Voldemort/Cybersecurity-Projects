// ©AngelaMos | 2026
// mod.rs

pub mod models;
pub mod queries;

use sqlx::PgPool;

pub async fn run_migrations(
    pool: &PgPool,
) -> Result<(), sqlx::migrate::MigrateError> {
    sqlx::migrate!("./migrations").run(pool).await
}
