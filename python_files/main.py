import tkinter as tk
from tkinter import messagebox
import model  # Ton module d'accès à la base de données


def refresh_kartings():
    """Rafraîchit l'affichage des kartings et des résultats triés selon la course sélectionnée."""
    for widget in frame.winfo_children():
        widget.destroy()

    def load_data():
        karts = model.read_table("Karts")
        races = model.read_table("Races")
        pilots = model.read_table("Pilots")
        pilots_has_karts = model.read_table("Pilots_has_Karts")
        pilots_has_results = model.read_table("Pilots_has_Results")
        results = model.read_table("Results")

        if not all([karts, races, pilots, pilots_has_results, results]):
            if not karts:
                tk.Label(frame, text="La base 'Karts' est vide.", font=("Arial", 12)).pack()
            if not races:
                tk.Label(frame, text="La base 'Races' est vide.", font=("Arial", 12)).pack()
            if not pilots:
                tk.Label(frame, text="La base 'Pilots' est vide.", font=("Arial", 12)).pack()
            if not pilots_has_results:
                tk.Label(frame, text="La base 'Pilots_has_Results' est vide.", font=("Arial", 12)).pack()
            if not results:
                tk.Label(frame, text="La base 'Results' est vide.", font=("Arial", 12)).pack()
            return None
        return karts, races, pilots, pilots_has_karts, pilots_has_results, results

    data = load_data()
    if not data:
        return

    karts, races, pilots, pilots_has_karts, pilots_has_results, results = data

    # --- Mise à jour du menu déroulant des courses ---
    race_name_map = {str(race["id"]): f"{race['location']} - {race['date']}" for race in races}
    menu = race_dropdown["menu"]
    menu.delete(0, "end")
    for race_id, label in race_name_map.items():
        menu.add_command(label=label, command=lambda rid=race_id: selected_race.set(rid))

    # --- Affichage des kartings ---
    tk.Label(frame, text="Kartings :", font=("Arial", 14, "bold")).pack(pady=(5, 5))
    for kart in karts:
        karting_id = kart["id"]
        karting_number = kart.get("number", "Inconnu")

        pilot_name = "Aucun pilote"
        for link in pilots_has_karts:
            if link["Karts_id"] == karting_id:
                pilot_id = link["Pilots_id"]
                pilot = next((p for p in pilots if p["id"] == pilot_id), None)
                if pilot:
                    pilot_name = pilot.get("Firstname", "Nom inconnu")
                break

        row_frame = tk.Frame(frame)
        row_frame.pack(fill="x", padx=5, pady=2)

        info_text = f"{karting_id}: Kart n°{karting_number} | Pilote: {pilot_name}"
        tk.Label(row_frame, text=info_text, font=("Arial", 12)).pack(side="left", padx=5)

        btn_delete = tk.Button(row_frame, text="Delete", command=lambda kid=karting_id: delete_karting(kid), bg="red", fg="white")
        btn_delete.pack(side="right", padx=5)

    # --- Affichage des résultats filtrés par course ---
    tk.Label(frame, text="Résultats de course :", font=("Arial", 14, "bold")).pack(pady=(15, 5))

    selected_race_id = selected_race.get()
    if selected_race_id.isdigit():
        race_results_ids = [res["id"] for res in results if str(res["Races_id"]) == selected_race_id]
        filtered_results = [r for r in pilots_has_results if r["Results_id"] in race_results_ids]
        sorted_results = sorted(filtered_results, key=lambda r: r.get("position", float("inf")))

        for result in sorted_results:
            pilot_id = result["Pilots_id"]
            pilot = next((p for p in pilots if p["id"] == pilot_id), None)
            if pilot:
                nom = pilot.get("Lastname", "Nom inconnu")
                prenom = pilot.get("Firstname", "Prénom inconnu")
                position = result.get("position", "N/A")
                temps = result.get("time", "N/A")

                result_text = f"Position {position} : {prenom} {nom} - Temps : {temps}"
                tk.Label(frame, text=result_text, font=("Arial", 12)).pack(anchor="w", padx=10)
    else:
        tk.Label(frame, text="Sélectionnez une course pour voir les résultats.", font=("Arial", 12, "italic")).pack(pady=5)


def delete_karting(karting_id):
    """Supprime un karting après confirmation."""
    if messagebox.askyesno("Confirmation", f"Supprimer le karting ID {karting_id} ?"):
        model.delete_row("Karts", {"id": karting_id})
        refresh_kartings()


def add_karting():
    """Ajoute un karting à la base de données."""
    number = entry_number.get().strip()

    if not number.isdigit():
        messagebox.showwarning("Erreur", "Le numéro doit être un entier !")
        return

    success = model.insert_row("Karts", {"number": int(number)})
    if success:
        messagebox.showinfo("Succès", "Karting ajouté avec succès !")
        entry_number.delete(0, tk.END)
        refresh_kartings()
    else:
        messagebox.showerror("Erreur", "Impossible d'ajouter le karting.")


# --- Interface utilisateur ---
root = tk.Tk()
root.title("Kartings Manager")
root.geometry("600x600")

# Menu déroulant pour sélectionner une course
selected_race = tk.StringVar()
selected_race.set("0")  # Valeur par défaut invalide

tk.Label(root, text="Sélectionnez une course :", font=("Arial", 12)).pack(pady=(10, 0))
race_dropdown = tk.OptionMenu(root, selected_race, "")
race_dropdown.pack(pady=5)

selected_race.trace("w", lambda *args: refresh_kartings())

# Bouton Refresh
btn_refresh = tk.Button(root, text="Refresh", command=refresh_kartings, bg="blue", fg="white")
btn_refresh.pack(pady=5)

# Frame d'affichage
frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Formulaire d'ajout de karting
form_frame = tk.Frame(root, pady=10)
form_frame.pack(fill="x")

tk.Label(form_frame, text="Numéro:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=2)
entry_number = tk.Entry(form_frame, font=("Arial", 12))
entry_number.grid(row=0, column=1, padx=5, pady=2)

btn_add = tk.Button(form_frame, text="Ajouter", command=add_karting, bg="green", fg="white")
btn_add.grid(row=2, columnspan=2, pady=5)

# Chargement initial
refresh_kartings()
root.mainloop()
