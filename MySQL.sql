/* misc SQL code */

/* reviews table */
CREATE TABLE `pitchfork_reviews` (
  `url` text,
  `title` varchar(500) DEFAULT NULL,
  `score` varchar(10) DEFAULT NULL,
  `genre` varchar(50) DEFAULT NULL,
  `review` text,
  `get_date` datetime DEFAULT NULL,
  `error` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


/* urls table */
CREATE TABLE `popular_album_urls` (
  `url` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


/* update reviews */
UPDATE pitchfork_reviews
SET title = ''
	,score = ''
	,genre = ''
    ,review = ''
    ,get_date = NOW()
    ,error = null
WHERE url = 'https://pitchfork.com/reviews/albums/19851-dads-ill-be-the-tornado/'


