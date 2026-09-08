from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

race_type = sa.Enum("director", "worker", "junior", name="racetype")


def upgrade() -> None:
    op.create_table(
        "profession",
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_profession")),
    )
    op.create_table(
        "skill",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skill")),
    )
    op.create_table(
        "warrior",
        sa.Column("race", race_type, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("level >= 1", name=op.f("ck_warrior_positive_level")),
        sa.ForeignKeyConstraint(
            ["profession_id"], ["profession.id"],
            name=op.f("fk_warrior_profession_id_profession"), ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_warrior")),
    )
    op.create_table(
        "skillwarriorlink",
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("warrior_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skill.id"],
            name=op.f("fk_skillwarriorlink_skill_id_skill"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["warrior_id"], ["warrior.id"],
            name=op.f("fk_skillwarriorlink_warrior_id_warrior"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("skill_id", "warrior_id", name=op.f("pk_skillwarriorlink")),
    )


def downgrade() -> None:
    op.drop_table("skillwarriorlink")
    op.drop_table("warrior")
    op.drop_table("skill")
    op.drop_table("profession")
    race_type.drop(op.get_bind(), checkfirst=True)
