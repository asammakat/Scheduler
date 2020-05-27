DROP TABLE IF EXISTS organization;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS availability_request;
DROP TABLE IF EXISTS availability_slot;
DROP TABLE IF EXISTS booked_date;
DROP TABLE IF EXISTS roster;
DROP TABLE IF EXISTS member_requests;

CREATE TABLE organization(
    org_id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE member(
  member_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE availability_request(
    avail_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    avail_request_name TEXT NOT NULL,
    start_request DATETIME NOT NULL,
    end_request DATETIME NOT NULL,
    org_id INTEGER NOT NULL,
    completed BIT DEFAULT FALSE,
    FOREIGN KEY (org_id) REFERENCES organization (org_id)
);

CREATE TABLE availability_slot(
    avail_slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    avail_slot_name TEXT NOT NULL,
    start_slot DATETIME NOT NULL,
    end_slot DATETIME NOT NULL,
    avail_request_id INTEGER NOT NULL,
    org_id INTEGER NOT NULL,
    FOREIGN KEY (avail_request_id) REFERENCES availability_request (avail_request_id),
    FOREIGN KEY (org_id) REFERENCES organization (org_id)
);

CREATE TABLE booked_date(
    booked_date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booked_date_name TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    org_id INTEGER NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organization (org_id)
);

CREATE TABLE roster(
    org_id INTEGER,
    member_id INTEGER,
    FOREIGN KEY (org_id) REFERENCES organization (org_id),
    FOREIGN KEY (member_id) REFERENCES member (member_id),
    PRIMARY KEY (org_id, member_id)
);

CREATE TABLE member_requests(
    member_id INTEGER,
    avail_request_id INTEGER,
    answered BIT DEFAULT FALSE,
    PRIMARY KEY (member_id, avail_request_id)
);