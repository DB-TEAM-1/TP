-- Drop tables if they exist
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
    date DATE NOT NULL, -- happenDt -> date
    location VARCHAR(100) NOT NULL, -- happenPlace -> location
    kindCd VARCHAR(10) NOT NULL,
    upKindCd VARCHAR(10) NOT NULL,
    upKindNm VARCHAR(20) NOT NULL,
    kindNm VARCHAR(30) NOT NULL,
    colorCd VARCHAR(30) NOT NULL,
    age VARCHAR(30) NOT NULL,
    weight VARCHAR(20) NOT NULL,
    sexCd VARCHAR(10) NOT NULL,
    neuterYn VARCHAR(10) NOT NULL,
    specialMark TEXT,
    processState VARCHAR(20) NOT NULL,
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
    popfile1 TEXT NOT NULL, -- image_url -> popfile1
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
    image_url TEXT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 