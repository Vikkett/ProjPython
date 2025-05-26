USE Projet_karting;

INSERT INTO pilots (id, firstname, lastname, pseudo, date_of_birth, pw_hash, level)
VALUES
  ('1', 'Exemple', '1','e1', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0'),
  ('2', 'Exemple', '2','e2', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0'),
  ('3', 'Exemple', '3','e3', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0'),
  ('4', 'Exemple', '4','e4', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0'),
  ('5', 'Exemple', '5','e5', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0'),
  ('6', 'Exemple', '6','e6', '1985-04-12', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', '0');

INSERT INTO races (id, location, date, Type)
VALUES
  ('1', 'Miami', '2025-05-10', 'Exhibition'),
  ('2', 'Austin', '2025-06-15', 'Qualifier'),
  ('3', 'Las Vegas', '2025-07-20', 'Championship'),
  ('4', 'New York', '2025-08-25', 'Semi-Final'),
  ('5', 'Los Angeles', '2025-09-30', 'Final');

INSERT INTO results (date, races_id)
VALUES
  ('2025-05-10', 1), 
  ('2025-06-15', 2), 
  ('2025-07-20', 3), 
  ('2025-08-25', 4),
  ('2025-09-30', 5); 


INSERT INTO karts (number)
VALUES
  (01),
  (02),
  (03),
  (04),
  (05),
  (06),
  (07),
  (08),
  (09),
  (010);

INSERT INTO pilots_has_results (Pilots_id, results_id, position, TIME)
VALUES 
	(1,1, 3,'03:46:24' ),
	(2,1, 5, '03:48:09'),
	(3,1, 2, '03:46:19'),
	(4,1, 4, '03:47:32'),
	(5,1, 1, '03:45:30');
	
USE projet_karting;
INSERT INTO pilots_has_karts (Pilots_id, Karts_id)
VALUES 
	(1,1),
	(2,2),
	(3,3),
	(4,4),
	(5,5),
	(1,6),
	(2,7),
	(3,8),
	(4,9),
	(5,10);