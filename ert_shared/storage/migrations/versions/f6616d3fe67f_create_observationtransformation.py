"""Create ObservationTransformation

Revision ID: f6616d3fe67f
Revises: c88293c7d72e
Create Date: 2021-02-15 12:54:16.821493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6616d3fe67f"
down_revision = "c88293c7d72e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "observation_transformation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("active_list", sa.PickleType(), nullable=False),
        sa.Column("scale_list", sa.PickleType(), nullable=False),
        sa.Column("observation_id", sa.Integer(), nullable=False),
        sa.Column("update_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["update_id"],
            ["update.id"],
        ),
        sa.ForeignKeyConstraint(
            ["observation_id"],
            ["observation.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###
    with op.batch_alter_table("update") as bop:
        bop.alter_column("ensemble_reference_id", nullable=True)
        bop.alter_column("ensemble_result_id", nullable=True)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("observation_transformation")
    # ### end Alembic commands ###
