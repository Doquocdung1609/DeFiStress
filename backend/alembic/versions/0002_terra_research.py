"""Add Terra historical research datasets and experiments."""

from alembic import op

from backend.app.db.models import Base

revision = "0002_terra_research"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    for table_name in (
        "terra_experiments",
        "model_benchmarks",
        "historical_replays",
        "terra_wallet_cohorts",
        "terra_hourly_state",
        "dataset_sources",
        "research_dataset_versions",
        "research_case_studies",
    ):
        op.drop_table(table_name)
