"""initial_schema

Revision ID: 7d5bfee8904b
Revises: 
Create Date: 2026-10-08 16:51:05.511935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d5bfee8904b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('salary_currency', sa.String(length=10), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('collected_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.create_index('ix_jobs_source', ['source'], unique=False)
        batch_op.create_index('ix_jobs_title', ['title'], unique=False)
        batch_op.create_index('ix_jobs_company_name', ['company_name'], unique=False)
        batch_op.create_index('ix_jobs_location', ['location'], unique=False)
        batch_op.create_index('ix_jobs_country', ['country'], unique=False)
        batch_op.create_index('ix_jobs_posted_at', ['posted_at'], unique=False)
        batch_op.create_index('ix_jobs_source_external_id', ['source', 'external_id'], unique=True)

    # companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.create_index('ix_companies_name', ['name'], unique=False)
        batch_op.create_index('ix_companies_normalized_name', ['normalized_name'], unique=True)

    # skills table
    op.create_table(
        'skills',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.create_index('ix_skills_name', ['name'], unique=True)
        batch_op.create_index('ix_skills_canonical_name', ['canonical_name'], unique=False)
        batch_op.create_index('ix_skills_category', ['category'], unique=False)

    # job_skills table
    op.create_table(
        'job_skills',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('extraction_method', sa.String(length=50), nullable=False, server_default='dictionary'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('job_skills', schema=None) as batch_op:
        batch_op.create_index('ix_job_skills_job_id', ['job_id'], unique=False)
        batch_op.create_index('ix_job_skills_skill_id', ['skill_id'], unique=False)
        batch_op.create_index('ix_job_skills_job_skill', ['job_id', 'skill_id'], unique=True)

    # candidate_skills table
    op.create_table(
        'candidate_skills',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('occurrences', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source_method', sa.String(length=50), nullable=False, server_default='llm'),
        sa.Column('approved', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('candidate_skills', schema=None) as batch_op:
        batch_op.create_index('ix_candidate_skills_name', ['name'], unique=False)

    # analysis_runs table
    op.create_table(
        'analysis_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('jobs_analyzed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('analysis_runs', schema=None) as batch_op:
        batch_op.create_index('ix_analysis_runs_created_at', ['created_at'], unique=False)

    # skill_demands table
    op.create_table(
        'skill_demands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('analysis_run_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('job_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('skill_demands', schema=None) as batch_op:
        batch_op.create_index('ix_skill_demands_analysis_run_id', ['analysis_run_id'], unique=False)
        batch_op.create_index('ix_skill_demands_skill_id', ['skill_id'], unique=False)
        batch_op.create_index('ix_skill_demands_run_skill', ['analysis_run_id', 'skill_id'], unique=True)

    # user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True, server_default='India'),
        sa.Column('preferred_locations', sa.Text(), nullable=True),
        sa.Column('target_roles', sa.Text(), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True, server_default='0-2 years'),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('user_profiles')
    op.drop_table('skill_demands')
    op.drop_table('analysis_runs')
    op.drop_table('candidate_skills')
    op.drop_table('job_skills')
    op.drop_table('skills')
    op.drop_table('companies')
    op.drop_table('jobs')
