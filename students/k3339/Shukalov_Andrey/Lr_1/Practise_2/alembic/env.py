from alembic import context
from sqlmodel import SQLModel

import models
from connection import engine, get_database_url


config = context.config
target_metadata = SQLModel.metadata


def configure_and_run(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    supplied_connection = config.attributes.get("connection")
    if supplied_connection is not None:
        configure_and_run(supplied_connection)
    else:
        with engine.connect() as connection:
            configure_and_run(connection)
