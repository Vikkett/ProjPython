# Exemple de connection à une BD
# il faut avoir installé mysqlconnector (pip install mysql-connector-python)
# JCY pour classe SI-CA1a
# mars 2025


import mysql.connector


def open_db():
    """Établit une connexion à la base de données et retourne l'objet connexion."""
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port='3306',
            user='root',
            password='root',
            database="Projet_karting"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de connexion : {err}")
        return None


def read_SQL(sql, params=None):
    """Exécute une requête SELECT et retourne les résultats (avec ou sans paramètres)."""
    conn = open_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Erreur SQL : {err}")
        return []
    finally:
        cursor.close()
        conn.close()



def read_table(table):
    """Lit le contenu d'une table et retourne une liste de dictionnaires."""
    return read_SQL(f"SELECT * FROM {table}")


def exec_SQL(sql):
    """
    Exécute une requête SQL (INSERT, UPDATE, DELETE, etc.).

    :param sql: Chaîne contenant la requête SQL complète.
    :return: True si la requête s'exécute avec succès, sinon False.
    """
    conn = open_db()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print(f"Requête exécutée avec succès : {sql}")
        return True
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'exécution de la requête : {err}")
        return False
    finally:
        cursor.close()
        conn.close()


def insert_row(table, values):
    """
    Insère un seul enregistrement dans une table.

    :param table: Nom de la table.
    :param values: Dictionnaire représentant une seule ligne à insérer.
                   Ex: {"name": "Concert 1", "datetime": "2025-06-15 20:00:00"}
    """
    if not values:
        print("Aucune donnée à insérer.")
        return False

    conn = open_db()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Générer les colonnes et les placeholders (%s, %s, ...)
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["%s"] * len(values))

        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        data = tuple(values.values())
        print(sql, data)
        cursor.execute(sql, data)
        conn.commit()
        print(f"Enregistrement inséré avec l'ID {cursor.lastrowid}.")
        return True
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'insertion dans {table} : {err}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_row(table, new_values, where):
    """
    Met à jour une ligne dans une table.

    :param table: Nom de la table.
    :param new_values: Dictionnaire des colonnes et nouvelles valeurs {"colonne": valeur}.
    :param where: Dictionnaire des conditions {"colonne": valeur}.
    """
    if not new_values or not where:
        print("Données incomplètes pour la mise à jour.")
        return False

    conn = open_db()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Construire la requête
        set_clause = ", ".join([f"{key} = %s" for key in new_values.keys()])
        where_clause = " AND ".join([f"{key} = %s" for key in where.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        data = tuple(new_values.values()) + tuple(where.values())

        cursor.execute(sql, data)
        conn.commit()
        print(f"{cursor.rowcount} enregistrement(s) mis à jour.")
        return True
    except mysql.connector.Error as err:
        print(f"Erreur lors de la mise à jour dans {table} : {err}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_row(table, where):
    """
    Supprime un enregistrement d'une table.

    :param table: Nom de la table.
    :param where: Dictionnaire des conditions {"colonne": valeur}.
    """
    if not where:
        print("Une condition WHERE est obligatoire pour la suppression.")
        return False

    conn = open_db()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        where_clause = " AND ".join([f"{key} = %s" for key in where.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"

        cursor.execute(sql, tuple(where.values()))
        conn.commit()
        print(f"{cursor.rowcount} enregistrement(s) supprimé(s).")
        return True
    except mysql.connector.Error as err:
        print(f"Erreur lors de la suppression dans {table} : {err}")
        return False
    finally:
        cursor.close()
        conn.close()


# Exemples d'utilisation
if __name__ == "__main__":

    # Tests de exec_SQL
    # Mettre à jour un concert
    # exec_SQL("UPDATE concerts SET name = 'Rock Fest 2025' WHERE id = 3")

    # Supprimer un concert
    # exec_SQL("DELETE FROM concerts WHERE id = 3")

    # Test de insert_table avec un seul enregistrement
    new_concert = {"id": 10, "name": "Blues Night 4", "datetime": "2025-09-18 20:00:00"}
    # insert_row("concerts", new_concert)

    # Test de update_row Mettre à jour un concert
    # update_row("concerts", {"name": "Rock Fest 2025"}, {"id": 4})

    # Test de delete_row Supprimer un concert
    # delete_row("concerts", {"id": 10})

    # Test de read_SQL
    data = read_table("concerts")
    print(data)  # affichage complet
    for row in data:  # affichage ligne par ligne
        print(row)
