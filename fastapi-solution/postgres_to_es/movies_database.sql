CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.genre (
	id uuid PRIMARY KEY,
	name text NOT NULL,
	description text,
	created timestamp with time zone,
	modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.film_work (
	id uuid PRIMARY KEY,
	title text NOT NULL,
	description text,
	creation_date date,
	rating double precision,
	type text NOT NULL,
	created timestamp with time zone,
	modified timestamp with time zone,
	file_path text
);

CREATE TABLE IF NOT EXISTS content.person (
	id uuid PRIMARY KEY,
	full_name text NOT NULL,
	created timestamp with time zone,
	modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
	id uuid PRIMARY KEY,
	genre_id uuid REFERENCES content.genre (id) NOT NULL,
	film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
	created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
	id uuid PRIMARY KEY,
	person_id uuid REFERENCES content.person (id) NOT NULL,
	film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
	role text NOT NULL,
	created timestamp with time zone
);

CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);
CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);
CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);
