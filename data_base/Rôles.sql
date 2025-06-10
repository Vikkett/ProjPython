USE projet_karting;

CREATE ROLE If NOT EXISTS 'user';
-- Attribution de certaines autorisations
GRANT SELECT, INSERT, UPDATE, DELETE
  ON projet_karting.pilots TO 'user';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON projet_karting.pilots_has_races TO 'user';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON projet_karting.pilots_has_karts TO 'user';

-- Attribution du role utilisateur pour niveau 0
SELECT CONCAT('GRANT `user` TO `', pilots.Pseudo, '`;') AS grant_stmt
FROM projet_karting.pilots
WHERE LEVEL = 0;


CREATE ROLE If NOT EXISTS 'admin';
-- Attribution de toutes les autorisations
GRANT ALL ON projet_karting.* TO 'admin';
-- Attribution du role admin pour niveau 1
SELECT CONCAT('GRANT `admin` TO `', pilots.Pseudo, '`;') AS grant_stmt
FROM projet_karting.pilots
WHERE level = 1;

