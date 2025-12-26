CREATE TABLE IF NOT EXISTS grades (
    id         BIGSERIAL PRIMARY KEY,
    grade_date DATE     NOT NULL,
    group_no   TEXT     NOT NULL,
    full_name  TEXT     NOT NULL,
    grade      SMALLINT NOT NULL CHECK (grade BETWEEN 2 AND 5),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   pg_constraint
        WHERE  conname = 'uq_grades_natural_key'
    ) THEN
        ALTER TABLE grades
        ADD CONSTRAINT uq_grades_natural_key
        UNIQUE (grade_date, group_no, full_name, grade);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_grades_full_name ON grades (full_name);
CREATE INDEX IF NOT EXISTS idx_grades_grade_full_name ON grades (grade, full_name);

CREATE TABLE IF NOT EXISTS grades_stage (
    grade_date DATE     NOT NULL,
    group_no   TEXT     NOT NULL,
    full_name  TEXT     NOT NULL,
    grade      SMALLINT NOT NULL CHECK (grade BETWEEN 2 AND 5)
);

TRUNCATE TABLE grades_stage;
