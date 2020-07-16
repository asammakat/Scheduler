DROP TABLE IF EXISTS member_request CASCADE;
DROP TABLE IF EXISTS roster CASCADE;
DROP TABLE IF EXISTS booked_date CASCADE;
DROP TABLE IF EXISTS availability_slot CASCADE;
DROP TABLE IF EXISTS availability_request CASCADE;
DROP TABLE IF EXISTS organization CASCADE;
DROP TABLE IF EXISTS member CASCADE;

CREATE TABLE organization(
    org_id SERIAL PRIMARY KEY,
    org_name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE member(
  member_id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE availability_request(
    avail_request_id SERIAL PRIMARY KEY,
    avail_request_name TEXT NOT NULL,
    start_request TIMESTAMP NOT NULL,
    end_request TIMESTAMP NOT NULL,
    timezone TEXT NOT NULL,
    org_id INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (org_id) REFERENCES organization (org_id) ON DELETE CASCADE
);

CREATE TABLE availability_slot(
    avail_slot_id SERIAL PRIMARY KEY,
    start_slot TIMESTAMP NOT NULL,
    end_slot TIMESTAMP NOT NULL,
    avail_request_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL, 
    FOREIGN KEY (avail_request_id) REFERENCES availability_request (avail_request_id) ON DELETE CASCADE, 
    FOREIGN KEY (member_id) REFERENCES member (member_id) ON DELETE CASCADE
);

CREATE TABLE booked_date(
    booked_date_id SERIAL PRIMARY KEY,
    booked_date_name TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    timezone TEXT NOT NULL,
    org_id INTEGER NOT NULL,
    avail_request_id INTEGER,
    FOREIGN KEY (org_id) REFERENCES organization (org_id) ON DELETE CASCADE,
    FOREIGN KEY (avail_request_id) REFERENCES availability_request (avail_request_id) ON DELETE SET NULL
);

CREATE TABLE member_request(
    member_id INTEGER,
    avail_request_id INTEGER,
    answered BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (member_id) REFERENCES member (member_id) ON DELETE CASCADE,
    FOREIGN KEY (avail_request_id) REFERENCES availability_request (avail_request_id) ON DELETE CASCADE,
    PRIMARY KEY (member_id, avail_request_id)
);

CREATE TABLE roster(
    org_id INTEGER,
    member_id INTEGER,
    FOREIGN KEY (org_id) REFERENCES organization (org_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES member (member_id) ON DELETE CASCADE,
    PRIMARY KEY (org_id, member_id)
);