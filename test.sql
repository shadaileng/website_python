BEGIN TRANSACTION;
CREATE TABLE USER(
	ID NUMBER(50) PRIMARY KEY,
	NAME VARCHAR(50),
	PASSWORD VARCHAR(50),
	EMAIL VARCHAR(50),
	ADMIN NUMBER(2),
	IMAGE VARCHAR(50),
	CREATETIME VARCHAR(50),
	UPDATETIME VARCHAR(50)
);
CREATE TABLE BLOG(
	ID NUMBER(50) PRIMARY KEY,
	USERID NUMBER(50),
	NAME VARCHAR(50),
	SUMMARY VARCHAR(256),
	CONTENT VARCHAR(1024),
	CREATETIME VARCHAR(50),
	UPDATETIME VARCHAR(50)
);
CREATE TABLE COMMENT(
	ID NUMBER(50) PRIMARY KEY,
	USERID NUMBER(50),
	BLOGID NUMBER(50),
	CONTENT VARCHAR(140),
	CREATETIME VARCHAR(50),
	UPDATETIME VARCHAR(50)
);
COMMIT;
