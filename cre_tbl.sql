--# script to initialize the sqlite database used to record tweets.
-- meant to show what I did rather than be used in production

create table tweets(
ID integer primary key autoincrement,
msg char(280) not null,
link text,
tweeted int default 0
);

create table HNFP(
sakey integer primary key autoincrement,
rank integer not null,
post_title char(500) not null,
post_link char(300) not null,
cmnt1 text,
cmnt1_age char(20),
cmnt1_author char(15),
cmnt2 text,
cmnt2_age char(20),
cmnt2_author char(15),
tstamp char(16)
);
