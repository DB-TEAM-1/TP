-- Drop tables if they exist
DROP TABLE IF EXISTS "Review";
DROP TABLE IF EXISTS "Adoption";
DROP TABLE IF EXISTS "Report";
DROP TABLE IF EXISTS "Animal";
DROP TABLE IF EXISTS "Shelter";
DROP TABLE IF EXISTS "Users";

-- Create Users table (renamed from User to avoid reserved word)
CREATE TABLE "Users" (
    user_num SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_superuser BOOLEAN DEFAULT FALSE
);

-- Create Shelter table
CREATE TABLE "Shelter" (
    careRegNo VARCHAR(50) PRIMARY KEY,
    careNm VARCHAR(20) NOT NULL,
    orgNm VARCHAR(20) NOT NULL,
    divisionNm VARCHAR(20) NOT NULL,
    saveTrgtAnimal VARCHAR(20) NOT NULL,
    careAddr VARCHAR(50) NOT NULL,
    jibunAddr VARCHAR(50) NOT NULL,
    lat FLOAT,
    lng FLOAT,
    weekOprStime TIME,
    weekOprEtime TIME,
    weekendOprStime TIME,
    weekendOprEtime TIME,
    careTel VARCHAR(20) NOT NULL
);

-- Create Animal table
CREATE TABLE "Animal" (
    desertionNo VARCHAR(20) PRIMARY KEY,
    careRegNo VARCHAR(50) REFERENCES "Shelter"(careRegNo) ON DELETE CASCADE,
    happenDt DATE,
    happenPlace VARCHAR(100) NOT NULL,
    kindCd VARCHAR(10) NOT NULL,
    upKindCd VARCHAR(10) NOT NULL,
    upKindNm VARCHAR(20) NOT NULL,
    kindNm VARCHAR(30) NOT NULL,
    colorCd VARCHAR(30) NOT NULL,
    age VARCHAR(30) NOT NULL,
    weight VARCHAR(20) NOT NULL,
    sexCd VARCHAR(1) NOT NULL,
    neuterYn VARCHAR(1) NOT NULL,
    specialMark TEXT,
    processState VARCHAR(20) NOT NULL,
    endReason VARCHAR(30),
    updTm TIMESTAMP,
    rfidCd VARCHAR(30),
    popfile1 TEXT,
    vaccinationChk VARCHAR(1),
    healthChk VARCHAR(1),
    sfeSoci VARCHAR(1),
    sfeHealth VARCHAR(1)
);

-- Create Report table
CREATE TABLE "Report" (
    report_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "Users"(user_num) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "Shelter"(careRegNo) ON DELETE CASCADE,
    reported_dt DATE NOT NULL,
    reported_time TIME NOT NULL,
    location VARCHAR(100) NOT NULL,
    estimated_kind VARCHAR(50) NOT NULL,
    sex_cd VARCHAR(1) NOT NULL,
    image_url TEXT,
    status VARCHAR(20) NOT NULL,
    description TEXT NOT NULL
);

-- Create Adoption table
CREATE TABLE "Adoption" (
    adoption_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "Users"(user_num) ON DELETE CASCADE,
    desertionNo VARCHAR(20) REFERENCES "Animal"(desertionNo) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "Shelter"(careRegNo) ON DELETE CASCADE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL CHECK (status IN ('신청', '승인됨', '거절됨', '완료됨'))
);

-- Create Review table
CREATE TABLE "Review" (
    review_id SERIAL PRIMARY KEY,
    user_num INTEGER REFERENCES "Users"(user_num) ON DELETE CASCADE,
    desertionNo VARCHAR(20) REFERENCES "Animal"(desertionNo) ON DELETE CASCADE,
    careRegNo VARCHAR(50) REFERENCES "Shelter"(careRegNo) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    image_url TEXT,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 