import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import model
import login_register
from login_register import get_current_user

# Authentification obligatoire
current_user_pseudo, current_user_level = get_current_user()
if not current_user_pseudo:
    raise SystemExit("Accès refusé : vous devez être connecté pour accéder à cette interface.")

# Rafraîchissement des données et affichage
def refresh_kartings():
    for widget in frame.winfo_children():
        widget.destroy()

    def load_data():
        karts = model.read_table("Karts")
        races = model.read_table("Races")
        pilots = model.read_table("Pilots")
        pilots_has_karts = model.read_table("Pilots_has_Karts")
        pilots_has_races = model.read_table("Pilots_has_Races")
        pilots_has_results = model.read_table("Pilots_has_Results")
        results = model.read_table("Results")

        #if not all([karts, races, pilots, pilots_has_results, results]):
        if not all([races, pilots]):
            #if not karts: tk.Label(frame, text="La base 'Karts' est vide.", font=("Arial", 12)).pack()
            if not races: tk.Label(frame, text="La base 'Races' est vide.", font=("Arial", 12)).pack()
            if not pilots: tk.Label(frame, text="La base 'Pilots' est vide.", font=("Arial", 12)).pack()
            #if not pilots_has_results: tk.Label(frame, text="La base 'Pilots_has_Results' est vide.", font=("Arial", 12)).pack()
            #if not results: tk.Label(frame, text="La base 'Results' est vide.", font=("Arial", 12)).pack()
            return None
        return karts, races, pilots, pilots_has_karts, pilots_has_races, pilots_has_results, results

    data = load_data()
    if not data:
        return
    karts, races, pilots, pilots_has_karts, pilots_has_races, pilots_has_results, results = data

    # Filtrage par lieu/type/date
    filtered_races = races
    if selected_location.get():
        filtered_races = [r for r in filtered_races if r["location"] == selected_location.get()]
    if selected_type.get():
        filtered_races = [r for r in filtered_races if r["Type"] == selected_type.get()]
    if selected_date.get():
        filtered_races = [r for r in filtered_races if r["date"] == selected_date.get()]

    for race in filtered_races:
        tk.Label(frame, text=f"{race['location']} - {race['date']} ({race['Type']})", font=("Arial", 12)).pack(anchor="w")
        tk.Button(frame, text="Voir détails", command=lambda r=race: show_race_details(r)).pack(pady=2)

    # Mise à jour des filtres
    def update_menu(menu_widget, var, values):
        menu = menu_widget["menu"]
        menu.delete(0, "end")
        for val in values:
            menu.add_command(label=val, command=lambda v=val: var.set(v))

    update_menu(location_dropdown, selected_location, sorted(set(r["location"] for r in races)))
    update_menu(type_dropdown, selected_type, sorted(set(r["Type"] for r in races)))
    update_menu(date_dropdown, selected_date, sorted(set(r["date"] for r in races)))

# Affiche détails course ou permet inscription
def show_race_details(race):
    race_date = race["date"]
    now = datetime.now()
    race_id = race["id"]
    selected_race = race_id

    if race_date < now:
        results = model.read_SQL("""
            SELECT p.Pseudo, phr.position, phr.time
            FROM Pilots_has_Results phr
            JOIN Pilots p ON p.id = phr.Pilots_id
            JOIN Results r ON r.id = phr.Results_id
            WHERE r.Races_id = %s
            ORDER BY phr.position ASC
        """, (race_id,))

        if results:
            result_text = "\n".join([f"{r['position']} - {r['Pseudo']} ({r['time']})" for r in results])
            messagebox.showinfo("Résultats de la course", result_text)
        else:
            messagebox.showinfo("Résultats de la course", "Aucun résultat disponible.")
    else:
        if messagebox.askyesno("Inscription", f"Voulez-vous vous inscrire à la course : {race['location']} ?"):
            pilot = model.read_SQL("SELECT id FROM Pilots WHERE Pseudo = %s", (current_user_pseudo,))
            if not pilot:
                messagebox.showerror("Erreur", "Utilisateur introuvable.")
                return
            pilot_id = pilot[0]['id']
            result = model.insert_row("Pilots_has_races", {
                "Pilots_id": pilot_id,
                "Races_id": selected_race
            })
            if result:
                messagebox.showinfo("Succès", "Inscription réussie.")
            else:
                messagebox.showerror("Erreur", "Inscription échouée.")

# Affiche les résultats personnels de l'utilisateur connecté
def show_my_results():
    pseudo, _ = get_current_user()
    try:
        results = model.read_SQL("""
            SELECT r.name AS course_name, phr.position, phr.time
            FROM Pilots p
            JOIN Pilots_has_Results phr ON p.id = phr.Pilots_id
            JOIN Results res ON res.id = phr.Results_id
            JOIN Races r ON r.id = res.Races_id
            WHERE p.Pseudo = %s
            ORDER BY r.date DESC
        """, (pseudo,))
        if results:
            text = "\n".join([f"{r['course_name']}: Pos {r['position']}, Temps: {r['time']}" for r in results])
            messagebox.showinfo("Mes Résultats", text)
        else:
            messagebox.showinfo("Mes Résultats", "Aucun résultat trouvé.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def open_account_window():
    pseudo, _ = get_current_user()
    pilot_data = model.read_SQL("SELECT * FROM Pilots WHERE Pseudo = %s", (pseudo,))
    if not pilot_data:
        messagebox.showerror("Erreur", "Impossible de charger les données du compte.")
        return

    pilot = pilot_data[0]

    account_win = tk.Toplevel(root)
    account_win.title("Mon Compte")
    account_win.geometry("400x300")

    tk.Label(account_win, text="Modifier mes informations", font=("Arial", 14, "bold")).pack(pady=10)

    # Champs
    labels = ["Prénom", "Nom", "Date de naissance", "Pseudo"]
    keys = ["Firstname", "Lastname", "Date_of_birth", "Pseudo"]
    entries = {}

    for i, (label, key) in enumerate(zip(labels, keys)):
        tk.Label(account_win, text=label).pack()
        entry = tk.Entry(account_win)
        entry.insert(0, pilot.get(key) or "")
        entry.pack()
        entries[key] = entry

    def save_changes():
        pseudo = entries["Pseudo"].get().strip()
        something_updated = False

        for key in keys:
            new_val = entries[key].get().strip()

            # Ignore les champs vides
            if not new_val:
                continue

            # Traitement spécial pour la date de naissance
            if key == "Date_of_birth":
                try:
                    # Valide le format et convertit
                    parsed_date = datetime.strptime(new_val, "%Y-%m-%d")
                    new_val = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    messagebox.showerror("Erreur", "La date de naissance doit être au format AAAA-MM-JJ.")
                    return

            # Récupérer la valeur actuelle pour comparaison
            current_val_result = model.read_SQL(f"SELECT {key} FROM Pilots WHERE Pseudo = %s", (pseudo,))
            if not current_val_result:
                messagebox.showerror("Erreur", "Erreur lors de la lecture des données actuelles.")
                return

            current_value = str(current_val_result[0].get(key, "")).strip()

            # Si la nouvelle valeur est différente, on met à jour
            if current_value != new_val:
                update_result = model.update_row("Pilots", {key: new_val}, {"Pseudo": pseudo})
                if update_result:
                    something_updated = True
                else:
                    messagebox.showerror("Erreur", f"Échec de mise à jour du champ {key}.")
                    return

        if something_updated:
            messagebox.showinfo("Succès", "Informations mises à jour.")
            account_win.destroy()
        else:
            messagebox.showinfo("Aucune modification", "Aucune donnée n'a été modifiée.")

    def delete_account():
        confirm = messagebox.askyesno("Confirmation", "Supprimer définitivement votre compte ?")
        if confirm:
            model.delete_row("Pilots", {"Pseudo": pseudo})
            messagebox.showinfo("Compte supprimé", "Votre compte a été supprimé.")
            root.quit()

    tk.Button(account_win, text="Sauvegarder", command=save_changes, bg="green", fg="white").pack(pady=5)
    tk.Button(account_win, text="Supprimer mon compte", command=delete_account, bg="red", fg="white").pack(pady=5)


# Interface utilisateur principale
root = tk.Tk()
root.title("Kartings Manager")
root.geometry("600x600")

# --- Menu principal en haut à droite ---
menu_frame = tk.Frame(root)
menu_frame.pack(anchor="ne", padx=10, pady=5)

menu_button = tk.Menubutton(menu_frame, text="Menu", relief=tk.RAISED, font=("Arial", 11, "bold"))
menu = tk.Menu(menu_button, tearoff=0)

menu.add_command(label="🏠 Home", command=refresh_kartings)
menu.add_command(label="👤 Compte", command=lambda: open_account_window())

menu.add_separator()
menu.add_command(label="Quitter", command=root.quit)

menu_button.config(menu=menu)
menu_button.pack()


# Zone des filtres
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)

selected_location = tk.StringVar()
selected_type = tk.StringVar()
selected_date = tk.StringVar()

tk.Label(filter_frame, text="Lieu:").grid(row=0, column=0, padx=5)
location_dropdown = tk.OptionMenu(filter_frame, selected_location, "")
location_dropdown.grid(row=0, column=1, padx=5)

tk.Label(filter_frame, text="Type:").grid(row=0, column=2, padx=5)
type_dropdown = tk.OptionMenu(filter_frame, selected_type, "")
type_dropdown.grid(row=0, column=3, padx=5)

tk.Label(filter_frame, text="Date:").grid(row=0, column=4, padx=5)
date_dropdown = tk.OptionMenu(filter_frame, selected_date, "")
date_dropdown.grid(row=0, column=5, padx=5)

selected_location.trace_add("write", lambda *args: refresh_kartings())
selected_type.trace_add("write", lambda *args: refresh_kartings())
selected_date.trace_add("write", lambda *args: refresh_kartings())

# Bouton de mise à jour
tk.Button(root, text="Refresh", command=refresh_kartings, bg="blue", fg="white").pack(pady=5)

# Zone d’affichage principale
frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Chargement initial
refresh_kartings()
root.mainloop()
