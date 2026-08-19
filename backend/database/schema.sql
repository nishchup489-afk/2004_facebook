CREATE TABLE universities (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    name VARCHAR(150) NOT NULL UNIQUE,
    email_domain VARCHAR(100) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);




CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    university_id BIGINT NOT NULL,

    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,

    email VARCHAR(255) NOT NULL,

    password_hash TEXT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_users_university
        FOREIGN KEY (university_id)
        REFERENCES universities(id)
        ON DELETE RESTRICT
);




CREATE UNIQUE INDEX uq_users_email_lower
ON users (LOWER(email));





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
            OR
            requested_by = user_id_high
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
            LOWER(semester) IN (
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
    user_id BIGINT NOT NULL,

    course_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (
        user_id,
        course_id
    ),

    CONSTRAINT fk_enrollments_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enrollments_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);




CREATE INDEX idx_users_university
ON users (university_id);




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





CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
AS $$
BEGIN

    NEW.updated_at = NOW();

    RETURN NEW;

END;
$$
LANGUAGE plpgsql;





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