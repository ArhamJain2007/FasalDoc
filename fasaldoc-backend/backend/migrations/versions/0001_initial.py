"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("primary_crops", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("language", sa.String(2), nullable=False, server_default="en"),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # diseases
    op.create_table(
        "diseases",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("class_index", sa.Integer(), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("name_hi", sa.String(200), nullable=False),
        sa.Column("name_pa", sa.String(200), nullable=False),
        sa.Column("crop_en", sa.String(100), nullable=False),
        sa.Column("crop_hi", sa.String(100), nullable=False),
        sa.Column("crop_pa", sa.String(100), nullable=False),
        sa.Column("description_en", sa.Text(), nullable=False),
        sa.Column("description_hi", sa.Text(), nullable=False),
        sa.Column("description_pa", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
    )
    op.create_index("ix_diseases_class_index", "diseases", ["class_index"], unique=True)

    # treatments
    op.create_table(
        "treatments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("disease_id", sa.String(100), sa.ForeignKey("diseases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("name_hi", sa.String(200), nullable=False),
        sa.Column("name_pa", sa.String(200), nullable=False),
        sa.Column("dosage", sa.String(200), nullable=False),
        sa.Column("schedule", sa.Text(), nullable=False),
    )
    op.create_index("ix_treatments_disease_id", "treatments", ["disease_id"])

    # scans
    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("disease_class_index", sa.Integer(), nullable=False),
        sa.Column("disease_name", sa.String(200), nullable=False),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),
        sa.Column("image_url", sa.String(512), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("treatment_id", sa.String(36), nullable=True),
        sa.Column("synced_from_offline", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scans_user_id", "scans", ["user_id"])
    op.create_index("ix_scans_created_at", "scans", ["created_at"])

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("alert_type", sa.String(20), nullable=False),
        sa.Column("title_en", sa.String(300), nullable=False),
        sa.Column("title_hi", sa.String(300), nullable=False),
        sa.Column("title_pa", sa.String(300), nullable=False),
        sa.Column("body_en", sa.Text(), nullable=False),
        sa.Column("body_hi", sa.Text(), nullable=False),
        sa.Column("body_pa", sa.Text(), nullable=False),
        sa.Column("related_disease_id", sa.String(100), sa.ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_alerts_region", "alerts", ["region"])

    # fcm_tokens
    op.create_table(
        "fcm_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("platform", sa.String(10), nullable=False, server_default="android"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_fcm_tokens_token", "fcm_tokens", ["token"], unique=True)
    op.create_index("ix_fcm_tokens_user_id", "fcm_tokens", ["user_id"])
    op.create_index("ix_fcm_tokens_region", "fcm_tokens", ["region"])


def downgrade() -> None:
    op.drop_table("fcm_tokens")
    op.drop_table("alerts")
    op.drop_table("scans")
    op.drop_table("treatments")
    op.drop_table("diseases")
    op.drop_table("users")
