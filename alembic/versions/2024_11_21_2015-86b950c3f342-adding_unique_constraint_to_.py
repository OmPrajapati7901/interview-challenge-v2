"""Adding unique constraint to  BusinessSymptom

Revision ID: 86b950c3f342
Revises: 4823bf330265
Create Date: 2024-11-21 20:15:58.098029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86b950c3f342'
down_revision = '4823bf330265'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_business_symptom', 'business_symptoms', ['business_id', 'symptom_code', 'symptom_diagnostic'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_business_symptom', 'business_symptoms', type_='unique')
    # ### end Alembic commands ###
