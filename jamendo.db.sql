BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "artists" (
	"user_id"	INTEGER NOT NULL,
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"website"	TEXT,
	"image"	TEXT,
	PRIMARY KEY("user_id", "id")
);
CREATE TABLE IF NOT EXISTS "albums" (
	"user_id"	INTEGER NOT NULL,
	"id"	INTEGER NOT NULL,
	"name"	REAL NOT NULL,
	"artist_id"	INTEGER NOT NULL,
	"artist_name"	TEXT NOT NULL,
	"image"	TEXT,
	PRIMARY KEY("user_id","id")
);
CREATE TABLE IF NOT EXISTS "tracks" (
	"user_id"	INTEGER NOT NULL,
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"duration"	INTEGER,
	"position"	INTEGER,
	"album_id"	INTEGER NOT NULL,
	"album_name"	TEXT NOT NULL,
	"artist_id"	INTEGER NOT NULL,
	"artist_name"	TEXT NOT NULL,
	"album_image"	TEXT,
	"audiodownload"	TEXT NOT NULL,
	PRIMARY KEY("user_id","id")
);
COMMIT;
