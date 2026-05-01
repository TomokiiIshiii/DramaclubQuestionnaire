CREATE TABLE events(
    event_id integer PRIMARY KEY,
    event_name varchar(16) NOT NULL UNIQUE
);

CREATE TABLE performances(
    event_id integer NOT NULL,
    performance_id integer PRIMARY KEY,
    performance_name varchar(64) NOT NULL,
    CONSTRAINT Perf_event_id FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE chances(
    chance_id integer PRIMARY KEY,
    chance_text varchar(32) NOT NULL 
);

CREATE TABLE answers(
    answer_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id integer NOT NULL,
    performance_id integer NOT NULL,
    chance_id integer NOT NULL,
    answer_eval integer NOT NULL,
    answer_text varchar(512),
    answer_time timestamp(0) NOT NULL,
    CONSTRAINT Ans_event_id FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT Ans_performance_id FOREIGN KEY (performance_id) REFERENCES performances(performance_id),
    CONSTRAINT Ans_chance_id FOREIGN KEY (chance_id) REFERENCES chances(chance_id)
);  

INSERT INTO events (event_id, event_name) VALUES (1, '文化の祭典2026');

INSERT INTO performances (event_id, performance_id, performance_name) 
VALUES (1, 1, 'club Rain ～それは今宵限りの夢物語'), (1, 2, 'コロナ禍のヤクザ'), (1, 3, '雪解け');

INSERT INTO chances (chance_id, chance_text)
VALUES (1, 'ポスターから'), (2, 'SNSから'), (3, '友人から'), (4, 'OB・OG'), (5, 'その他');
