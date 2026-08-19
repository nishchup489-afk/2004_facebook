CREATE TABLE universities (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    email_domain VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE students (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    university_id BIGINT NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    university_email VARCHAR(255) NOT NULL,
    registration_number VARCHAR(150) NOT NULL,
    registration_code_hash TEXT NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    claimed_at TIMESTAMPTZ,

    CONSTRAINT fk_students_university
        FOREIGN KEY (university_id)
        REFERENCES universities(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_student_registration_number
        UNIQUE (
            university_id,
            registration_number
        )
);


CREATE UNIQUE INDEX uq_students_email_lower
ON students (LOWER(university_email));


CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    university_email VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_users_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE RESTRICT
);


CREATE UNIQUE INDEX uq_users_email_lower
ON users (LOWER(university_email));


CREATE TABLE profile (
    user_id BIGINT PRIMARY KEY,
    profile_pic TEXT,
    gender VARCHAR(30),
    status VARCHAR(50),
    residence TEXT,
    birth_date DATE,
    home_town VARCHAR(200),
    high_school VARCHAR(250),
    username VARCHAR(50) NOT NULL,
    mobile VARCHAR(30),
    websites JSONB,
    looking_for VARCHAR(100),
    interested_in VARCHAR(100),
    relationship_status VARCHAR(50),
    relationship_with BIGINT,
    political_views VARCHAR(100),
    interests JSONB,
    favorite_music JSONB,
    favorite_movies JSONB,
    bio TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_profile_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_profile_relationship_with
        FOREIGN KEY (relationship_with)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_relationship_not_self
        CHECK (
            relationship_with IS NULL
            OR relationship_with <> user_id
        )
);


CREATE UNIQUE INDEX uq_profile_username_lower
ON profile (LOWER(username));


CREATE TABLE friendships (
    user_id_low BIGINT NOT NULL,
    user_id_high BIGINT NOT NULL,
    requested_by BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,

    PRIMARY KEY (
        user_id_low,
        user_id_high
    ),

    CONSTRAINT chk_friend_order
        CHECK (
            user_id_low < user_id_high
        ),

    CONSTRAINT chk_friendship_status
        CHECK (
            status IN (
                'pending',
                'accepted',
                'rejected'
            )
        ),

    CONSTRAINT chk_requested_by
        CHECK (
            requested_by = user_id_low
            OR requested_by = user_id_high
        ),

    CONSTRAINT fk_friend_low
        FOREIGN KEY (user_id_low)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_friend_high
        FOREIGN KEY (user_id_high)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_friend_requester
        FOREIGN KEY (requested_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE courses (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    university_id BIGINT NOT NULL,
    course_code VARCHAR(30) NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    academic_year SMALLINT NOT NULL,
    semester VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_courses_university
        FOREIGN KEY (university_id)
        REFERENCES universities(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_course_semester
        CHECK (
            semester IN (
                'spring',
                'summer',
                'fall',
                'winter'
            )
        ),

    CONSTRAINT chk_academic_year
        CHECK (
            academic_year >= 1900
            AND academic_year <= 2200
        ),

    CONSTRAINT uq_course
        UNIQUE (
            university_id,
            course_code,
            academic_year,
            semester
        )
);


CREATE TABLE enrollments (
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (
        student_id,
        course_id
    ),

    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollments_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);


CREATE TABLE sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_students_university
ON students (university_id);


CREATE INDEX idx_students_name
ON students (
    last_name,
    first_name
);


CREATE INDEX idx_users_name
ON users (
    last_name,
    first_name
);


CREATE INDEX idx_enrollments_course
ON enrollments (course_id);


CREATE INDEX idx_friendships_low
ON friendships (
    user_id_low,
    status
);


CREATE INDEX idx_friendships_high
ON friendships (
    user_id_high,
    status
);


CREATE INDEX idx_courses_university
ON courses (university_id);


CREATE INDEX idx_sessions_user
ON sessions (user_id);


CREATE INDEX idx_sessions_expires_at
ON sessions (expires_at);


CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;


CREATE TRIGGER trg_students_updated_at
BEFORE UPDATE
ON students
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE
ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER trg_profile_updated_at
BEFORE UPDATE
ON profile
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();