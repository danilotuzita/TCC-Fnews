SELECT WORD_ID, WORD, AVG(PROBABILITY) PROBABILITY, COUNT(*) CNT
FROM WORDS_PROB WP, WORDS W
WHERE WP.WORD_ID = W.ID
GROUP BY WORD_ID
ORDER BY PROBABILITY/CNT;

SELECT P.ID PHRASE_ID,
       -- GROUP_CONCAT(W.WORD, ' ') PHRASE_WORDS
       GROUP_CONCAT(P.WORD_ORDER || ' - ' || W.WORD, ' ') PHRASE_WORDS
FROM PHRASES P, WORDS W
WHERE P.WORD_ID = W.ID
GROUP BY P.ID ORDER BY P.ID, P.WORD_ORDER;

SELECT P.ID PHRASE_ID, 
       GROUP_CONCAT(W.WORD, ' ') PHRASE_WORDS,
	   AVG(PROBABILITY) PROB,
	   COUNT(*) / 3 CNT
FROM PHRASES P, WORDS W, PHRASES_PROB PP
WHERE P.WORD_ID = W.ID
  AND P.ID = PP.PHRASE_ID
GROUP BY P.ID, PP.PHRASE_ID
ORDER BY PROB, CNT;

SELECT P.ID, P.WORD_ID, W.WORD, P.WORD_ORDER
FROM PHRASES P, WORDS W WHERE P.WORD_ID = W.ID
AND P.ID = 12;


SELECT ID FROM PHRASES
WHERE (WORD_ID = 13 AND WORD_ORDER = 0) 
   OR (WORD_ID = 14 AND WORD_ORDER = 1) 
   OR (WORD_ID =  2 AND WORD_ORDER = 2)
GROUP BY ID
HAVING COUNT(*) = 3;

-- VVVVVVVVVVV FUNFANDO VVVVVVVVVVV --
SELECT P.PHRASE_ID, P.PHRASE_WORDS, AVG(PROBABILITY) PROB, COUNT(*) CNT
FROM (
	-- SELECT PHRASE_ID, GROUP_CONCAT(WORD_ORDER || ' - ' || WORD, ' ') PHRASE_WORDS FROM (
	SELECT PHRASE_ID, GROUP_CONCAT(WORD, ' ') PHRASE_WORDS FROM (
		SELECT P.ID PHRASE_ID, W.ID WORD_ID, W.WORD, P.WORD_ORDER FROM PHRASES P, WORDS W WHERE P.WORD_ID = W.ID ORDER BY PHRASE_ID, WORD_ORDER
	)
	GROUP BY PHRASE_ID
) P, PHRASES_PROB PP
WHERE P.PHRASE_ID = PP.PHRASE_ID
GROUP BY P.PHRASE_ID
ORDER BY -CNT, -PROB;

'SELECT PROBABILITY FROM PHRASES_PROB WHERE PHRASE_ID = ' + + ';'

SELECT PHRASE_ID, AVG(PROBABILITY) PROB, COUNT(PHRASE_ID) CNT FROM PHRASES_PROB 
GROUP BY PHRASE_ID HAVING CNT >= Z AND PROB NOT BETWEEN X AND Y;

SELECT PHRASE_ID FROM PHRASES_PROB
GROUP BY PHRASE_ID 
HAVING COUNT(PHRASE_ID) >= Z 
   AND AVG(PROBABILITY) NOT BETWEEN X AND Y;

SELECT PHRASE_ID FROM PHRASES_PROB
WHERE PHRASE_ID = PID
GROUP BY PHRASE_ID 
HAVING COUNT(PHRASE_ID) >= Z 
   AND AVG(PROBABILITY) NOT BETWEEN X AND Y;

SELECT PHRASE_ID, PROBABILITY, COUNT(*) FROM PHRASES_PROB
WHERE PHRASE_ID = PID
GROUP BY PHRASE_ID, PROBABILITY;

SELECT COUNT(*) FROM PHRASES_PROB
WHERE PHRASE_ID = PID
AND PROBABILITY = PROB;

SELECT PHRASE_ID, COUNT(*) FROM PHRASES_PROB 
WHERE PROBABILITY = PROB
GROUP BY PHRASE_ID;
