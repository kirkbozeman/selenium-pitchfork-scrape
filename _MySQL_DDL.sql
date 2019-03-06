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



/* cleaned view */

CREATE VIEW pitchfork_reviews_clean AS

SELECT
url,
SUBSTRING(title,1,POSITION(': ' IN title)-1) AS artist,
SUBSTRING(title,POSITION(': ' IN title)+2,
		POSITION(' Album Review | Pitchfork' IN title)-POSITION(': ' IN title)-2
		) AS album,
#title,
score,
REPLACE(genre,'&amp;','&') AS genre,
review,
REPLACE(
	REPLACE(
		REPLACE(REPLACE(
			REPLACE(REPLACE(
				REPLACE(REPLACE(review,'<p>',''),'</p>',''),
					'<strong>',''),'</strong>',''),
						'<em>',''),'</em>',''),
							'<p class="bnm-txt">Best new music',''),
								'\n','') AS review_clean,
get_date,
error,
pub_date,
REPLACE(release_dt,' <!-- -->•<!-- --> <!-- -->','') AS release_dt,
label,
author
FROM Dev.pitchfork_reviews
ORDER BY get_date DESC

#WHERE review LIKE '%zeppelin%'



