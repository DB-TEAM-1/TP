-- Drop tables if they exist
DROP VIEW IF EXISTS review_full_info CASCADE;
DROP VIEW IF EXISTS report_full_info CASCADE;
DROP TABLE IF EXISTS "review";
DROP TABLE IF EXISTS "adoption";
DROP TABLE IF EXISTS "report";
DROP TABLE IF EXISTS "animal";
DROP TABLE IF EXISTS "shelter";
DROP TABLE IF EXISTS "users";

-- Create Users table (renamed from User to avoid reserved word)
CREATE TABLE "users" (
    user_num INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    id VARCHAR(20) NOT NULL,
    password VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Shelter table
CREATE TABLE "shelter" (
    careRegNo VARCHAR(50) PRIMARY KEY,
    careNm VARCHAR(20) NOT NULL,
    orgNm VARCHAR(20) NOT NULL,
    divisionNm VARCHAR(20) NOT NULL,
    saveTrgtAnimal VARCHAR(20),
    careAddr VARCHAR(100) NOT NULL,
    jibunAddr VARCHAR(100) NOT NULL,
    lat FLOAT,
    lng FLOAT,
    weekOprStime TIME,
    weekOprEtime TIME,
    weekendOprStime TIME,
    weekendOprEtime TIME,
    careTel VARCHAR(20) NOT NULL
);

-- Create Animal table
CREATE TABLE "animal" (
    desertionNo VARCHAR(20) PRIMARY KEY,
    careRegNo VARCHAR(50) REFERENCES "shelter"(careRegNo) ON DELETE CASCADE,
    date DATE, -- happenDt -> date
    location VARCHAR(100), -- happenPlace -> location
    kindCd VARCHAR(10),
    upKindCd VARCHAR(10),
    upKindNm VARCHAR(20),
    kindNm VARCHAR(30),
    colorCd VARCHAR(30),
    age VARCHAR(30),
    weight VARCHAR(20),
    sexCd VARCHAR(10),
    neuterYn VARCHAR(10),
    specialMark TEXT,
    processState VARCHAR(20),
    endReason VARCHAR(70),
    updTm TIMESTAMP,
    rfidCd VARCHAR(30),
    popfile1 TEXT,
    vaccinationChk VARCHAR(100),
    healthChk VARCHAR(100),
    sfeSoci VARCHAR(70),
    sfeHealth VARCHAR(70)
);

-- Create Report table
CREATE TABLE "report" (
    report_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "users"(user_num) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "shelter"(careRegNo) ON DELETE CASCADE,
    date DATE NOT NULL, -- reported_dt -> date
    location VARCHAR(100) NOT NULL,
    kindNm VARCHAR(30) NOT NULL, -- estimated_kind VARCHAR(50) NOT NULL -> kindNm VARCHAR(30) NOT NULL
    sexCd VARCHAR(1) NOT NULL, -- sex_cd -> sexCd
    image_url TEXT NOT NULL, -- popfile1 -> image_url
    status VARCHAR(20) NOT NULL,
    description TEXT NOT NULL
);

-- Create Adoption table
CREATE TABLE "adoption" (
    adoption_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "users"(user_num) ON DELETE CASCADE,
    desertionNo VARCHAR(20) REFERENCES "animal"(desertionNo) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "shelter"(careRegNo) ON DELETE CASCADE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL CHECK (status IN ('신청', '승인됨', '거절됨', '완료됨'))
);

-- Create Review table
CREATE TABLE "review" (
    review_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "users"(user_num) ON DELETE CASCADE,
    desertionNo VARCHAR(20) REFERENCES "animal"(desertionNo) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "shelter"(careRegNo) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create report_full_info View
CREATE VIEW report_full_info AS
SELECT
    r.report_id,
    r.user_num,
    r.careregno,
    r.date,
    TO_CHAR(r.date, 'YYYY-MM-DD HH24:MI') as formatted_date,
    r.location,
    r.kindnm,
    r.sexcd,
    r.image_url,
    r.status,
    r.description,
    u.name as reporter_name,
    s.carenm as shelter_name
FROM
    report r
LEFT JOIN
    users u ON r.user_num = u.user_num
LEFT JOIN
    shelter s ON r.careregno = s.careregno;

-- Create review_full_info View
CREATE VIEW review_full_info AS
SELECT
    rv.review_id,
    rv.user_num,
    rv.desertionNo,
    rv.comment,
    rv.image_url,
    rv.created_at as date,
    TO_CHAR(rv.created_at, 'YYYY-MM-DD HH24:MI') as formatted_date,
    rv.rating,
    u.name as reviewer_name,
    a.kindnm,
    a.popfile1 as animal_image_url,
    s.carenm as shelter_name
FROM
    review rv
LEFT JOIN
    users u ON rv.user_num = u.user_num
LEFT JOIN
    animal a ON rv.desertionNo = a.desertionNo
LEFT JOIN
    shelter s ON rv.careregno = s.careregno; 