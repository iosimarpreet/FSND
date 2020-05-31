"""empty message

Revision ID: c21e42098d7b
Revises: 1038fbb243b3
Create Date: 2020-05-30 19:25:59.433982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c21e42098d7b'
down_revision = '1038fbb243b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venue_genres')
    op.drop_table('artist_genres')
    op.drop_table('genres')
    op.add_column('artists', sa.Column('genre', sa.String(), nullable=True))
    op.add_column('venues', sa.Column('genre', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'genre')
    op.drop_column('artists', 'genre')
    op.create_table('artist_genres',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['venues.id'], name='artist_genres_artist_id_fkey'),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], name='artist_genres_genre_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='artist_genres_pkey')
    )
    op.create_table('genres',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('genres_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='genres_pkey'),
    sa.UniqueConstraint('name', name='genres_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('venue_genres',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], name='venue_genres_genre_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], name='venue_genres_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='venue_genres_pkey')
    )
    # ### end Alembic commands ###
