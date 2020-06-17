DROP TABLE IF EXISTS year_list;

DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS education;
DROP TABLE IF EXISTS skill;
DROP TABLE IF EXISTS workinfo;

DROP TABLE IF EXISTS school;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS class;
DROP TABLE IF EXISTS rank;

CREATE TABLE year_list(
    year_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year TEXT NOT NULL
);

CREATE TABLE person(
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    id_number TEXT NOT NULL,
    phone TEXT NOT NULL,
    political_status TEXT NOT NULL,
    time_Party TEXT NOT NULL,
    time_work TEXT NOT NULL,
    address TEXT NOT NULL,
    resume TEXT NOT NULL
);

CREATE TABLE education(
    education_id INTEGER PRIMARY KEY AUTOINCREMENT,
    edu_start TEXT NOT NULL,
    time_edu_start TEXT NOT NULL,
    school_edu_start TEXT NOT NULL,
    major_edu_start TEXT NOT NULL,
    edu_end TEXT NOT NULL,
    time_edu_end TEXT NOT NULL,
    school_edu_end TEXT NOT NULL,
    major_edu_end TEXT NOT NULL,
    person_id INTEGER NOT NULL,
    FOREIGN KEY(person_id) REFERENCES person(person_id)
);

CREATE TABLE skill(
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_title TEXT NOT NULL,
    time_skill TEXT NOT NULL,
    skill_unit TEXT NOT NULL,
    skill_number TEXT NOT NULL,
    person_id INTEGER NOT NULL,
    FOREIGN KEY(person_id) REFERENCES person(person_id)
);

CREATE TABLE workinfo(
    workinfo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_school TEXT NOT NULL,
    work_kind TEXT NOT NULL,
    job_post TEXT NOT NULL,
    time_retire TEXT NOT NULL,
    person_id INTEGER NOT NULL,
    FOREIGN KEY(person_id) REFERENCES person(person_id)
);


CREATE TABLE school(
    school_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name text unique NOT NULL
);


CREATE TABLE job(
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name text unique NOT NULL,
    school_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    FOREIGN KEY(school_id) REFERENCES school(school_id),
    FOREIGN KEY(person_id) REFERENCES person(person_id)
);

CREATE TABLE class(
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name text unique NOT NULL,
    school_id INTEGER NOT NULL,
    FOREIGN KEY(school_id) REFERENCES school(school_id)
);

CREATE TABLE rank(
    subject TEXT NOT NULL,
    class_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    rank1 TEXT NOT NULL,
    PRIMARY KEY(class_id, subject, person_id),
    FOREIGN KEY(class_id) REFERENCES class(class_id),
    FOREIGN KEY(person_id) REFERENCES person(person_id)
)
