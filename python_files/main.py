"""
Author: Viktoriia Varennyk et Niels Delafontaine
Date: 07.04.2025
Name: Projet_karting
Version: 0.4
------------------------------------------------------------------------------------------------------------------------
Modifications:
Date:
By:
Comment:
Fixed subscription list to show all registered events including past ones by removing date filtering.
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import model  # module d'accès à la base de donnée
import login_register
from login_register import get_current_user  # module de login
from PIL import Image, ImageTk


def open_main_window(current_user_pseudo, current_user_level):
    global root
    root = tk.Tk()
    root.title("Kartings Manager")
    root.geometry("600x600")

    # Create a frame over the background to hold all widgets
    main_frame = tk.Frame(root, bg="white")
    main_frame.place(relwidth=1, relheight=1)

    # --- Menu principal en haut à droite ---
    menu_frame = tk.Frame(main_frame)
    menu_frame.pack(anchor="ne", padx=10, pady=5)

    menu_button = tk.Menubutton(menu_frame, text="Menu", relief=tk.RAISED, font=("Arial", 11, "bold"))
    menu = tk.Menu(menu_button, tearoff=0)
    menu.add_command(label="🏠 Home", command=refresh_kartings)
    menu.add_command(label="👤 Compte", command=lambda: open_account_window())
    menu.add_command(label="🏆 Mes Résultats", command=show_my_results)
    menu.add_command(label="📋 Mes Inscriptions", command=show_my_subscriptions)

    menu.add_separator()
    menu.add_command(label="Quitter", command=root.quit)
    menu_button.config(menu=menu)
    menu_button.pack()

    # Zone des filtres
    filter_frame = tk.Frame(main_frame)
    filter_frame.pack(pady=10)

    global selected_location, selected_type, selected_date
    selected_location = tk.StringVar()
    selected_type = tk.StringVar()
    selected_date = tk.StringVar()

    tk.Label(filter_frame, text="Lieu:").grid(row=0, column=0, padx=5)
    global location_dropdown
    location_dropdown = tk.OptionMenu(filter_frame, selected_location, "")
    location_dropdown.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Type:").grid(row=0, column=2, padx=5)
    global type_dropdown
    type_dropdown = tk.OptionMenu(filter_frame, selected_type, "")
    type_dropdown.grid(row=0, column=3, padx=5)

    tk.Label(filter_frame, text="Date:").grid(row=0, column=4, padx=5)
    global date_dropdown
    date_dropdown = tk.OptionMenu(filter_frame, selected_date, "")
    date_dropdown.grid(row=0, column=5, padx=5)

    selected_location.trace_add("write", lambda *args: refresh_kartings())
    selected_type.trace_add("write", lambda *args: refresh_kartings())
    selected_date.trace_add("write", lambda *args: refresh_kartings())

    # Bouton de mise à jour
    tk.Button(main_frame, text="Refresh", command=refresh_kartings, bg="blue", fg="white").pack(pady=5)

    # Zone d’affichage principale
    global frame
    frame = tk.Frame(main_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Chargement initial
    refresh_kartings()

    root.mainloop()


def register_to_race(race):
    pseudo = login_register.current_user_pseudo
    if not pseudo:
        messagebox.showerror("Erreur", "Utilisateur non connecté.")
        return

    pilot_res = model.read_SQL("SELECT id FROM Pilots WHERE Pseudo = %s", (pseudo,))
    if not pilot_res:
        messagebox.showerror("Erreur", "Utilisateur introuvable.")
        return
    pilot_id = pilot_res[0]['id']

    race_id = race.get("id")
    if race_id is None:
        messagebox.showerror("Erreur", "ID de la course invalide.")
        return

    existing = model.read_SQL(
        "SELECT COUNT(*) AS count FROM Pilots_has_Races WHERE Pilots_id = %s AND Races_id = %s",
        (pilot_id, race_id)
    )
    already_registered = False
    if existing:
        try:
            already_registered = existing[0].get("count", 0) > 0
        except Exception:
            already_registered = False

    if already_registered:
        messagebox.showinfo("Information", "Vous êtes déjà inscrit à cette course.")
        return

    if messagebox.askyesno("Inscription", f"Voulez-vous vous inscrire à la course : {race.get('location', 'N/A')} ?"):
        result = model.insert_row(
            "Pilots_has_Races",
            {
                "Pilots_id": pilot_id,
                "Races_id": race_id,
            },
        )
        if result:
            messagebox.showinfo("Succès", "Inscription réussie.")
        else:
            messagebox.showerror("Erreur", "Inscription échouée.")


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

        if not all([races, pilots]):
            if not races:
                tk.Label(frame, text="La base 'Races' est vide.", font=("Arial", 12)).pack()
            if not pilots:
                tk.Label(frame, text="La base 'Pilots' est vide.", font=("Arial", 12)).pack()
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
        frame_race = tk.Frame(frame)
        frame_race.pack(fill="x", pady=2)

        race_label = tk.Label(frame_race, text=f"{race['location']} - {race['date']} ({race['Type']})", font=("Arial", 12))
        race_label.pack(side="left", anchor="w", fill="x", expand=True)

        btn_details = tk.Button(frame_race, text="Voir détails", command=lambda r=race: show_race_details(r))
        btn_details.pack(side="left", padx=5)

        btn_inscr = tk.Button(frame_race, text="S'inscrire", command=lambda r=race: register_to_race(r), bg="green", fg="white")
        btn_inscr.pack(side="left", padx=5)

    def update_menu(menu_widget, var, values):
        menu = menu_widget["menu"]
        menu.delete(0, "end")
        for val in values:
            menu.add_command(label=val, command=lambda v=val: var.set(v))

    update_menu(location_dropdown, selected_location, sorted(set(r["location"] for r in races)))
    update_menu(type_dropdown, selected_type, sorted(set(r["Type"] for r in races)))
    update_menu(date_dropdown, selected_date, sorted(set(r["date"] for r in races)))


def show_race_details(race):
    details = (
        f"Lieu : {race.get('location', 'N/A')}\n"
        f"Date : {race.get('date', 'N/A')}\n"
        f"Type : {race.get('Type', 'N/A')}\n"
    )
    messagebox.showinfo("Détails de la course", details)


def show_my_results():
    pseudo, _ = get_current_user()
    try:
        results = model.read_SQL(
            """
            SELECT r.name AS course_name, phr.position, phr.time
            FROM Pilots p
            JOIN Pilots_has_Results phr ON p.id = phr.Pilots_id
            JOIN Results res ON res.id = phr.Results_id
            JOIN Races r ON r.id = res.Races_id
            WHERE p.Pseudo = %s
            ORDER BY r.date DESC
        """,
            (pseudo,),
        )
        if results:
            text = "\n".join([f"{r['course_name']}: Pos {r['position']}, Temps: {r['time']}" for r in results])
            messagebox.showinfo("Mes Résultats", text)
        else:
            messagebox.showinfo("Mes Résultats", "Aucun résultat trouvé.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


def open_account_window():
    # (existing code here)
    pass


def show_my_subscriptions():
    pseudo, _ = get_current_user()

    pilot = model.read_SQL("SELECT id FROM Pilots WHERE Pseudo = %s", (pseudo,))
    if not pilot:
        messagebox.showerror("Erreur", "Utilisateur non trouvé.")
        return

    pilot_id = pilot[0]["id"]

    # Modified query to show all subscriptions including past events
    subscriptions = model.read_SQL(
        """
        SELECT r.id, r.location, r.date, r.Type
        FROM Pilots_has_Races phr
        JOIN Races r ON r.id = phr.Races_id
        WHERE phr.Pilots_id = %s
        ORDER BY r.date ASC
    """,
        (pilot_id,),
    )

    if not subscriptions:
        messagebox.showinfo("Inscriptions", "Vous n'êtes inscrit à aucune course.")
        return

    subs_win = tk.Toplevel(root)
    subs_win.title("Mes Inscriptions")
    subs_win.geometry("500x400")

    tk.Label(subs_win, text="Courses inscrites", font=("Arial", 14, "bold")).pack(pady=10)

    for race in subscriptions:
        # Note: We no longer skip past dates here, so all registered events will show
        race_date = race["date"]
        if isinstance(race_date, str):
            try:
                race_date_dt = datetime.strptime(race_date, "%Y-%m-%d")
            except ValueError:
                race_date_dt = None
        else:
            race_date_dt = race_date

        race_info = f"{race['location']} - "
        if race_date_dt:
            race_info += race_date_dt.strftime('%Y-%m-%d')
        else:
            race_info += str(race_date)
        race_info += f" ({race['Type']})"

        frame_race = tk.Frame(subs_win, pady=5)
        frame_race.pack(fill="x", padx=10)

        tk.Label(frame_race, text=race_info, anchor="w").pack(side="left", fill="x", expand=True)

        def make_unsubscribe_button(race_id):
            return lambda: unsubscribe_from_race(pilot_id, race_id, subs_win)

        tk.Button(frame_race, text="Se désinscrire", command=make_unsubscribe_button(race["id"]), bg="red", fg="white").pack(
            side="right"
        )


def unsubscribe_from_race(pilot_id, race_id, window_to_close):
    confirm = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir vous désinscrire ?")
    if confirm:
        result = model.delete_row("Pilots_has_Races", {"Pilots_id": pilot_id, "Races_id": race_id})
        if result:
            messagebox.showinfo("Succès", "Vous avez été désinscrit.")
            window_to_close.destroy()
            show_my_subscriptions()  # Refresh list
        else:
            messagebox.showerror("Erreur", "Échec de la désinscription.")

