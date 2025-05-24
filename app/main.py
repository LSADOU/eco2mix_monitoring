import tkinter as tk
import api_eco2mix
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def exit():
    #Permet de bien fermer toutes les figures pour ne pas avoir de processus encore actifs apres la fermeture de l'interface
    plt.close('all')
    root.destroy()

root = tk.Tk()
root.title("Eco2mix monitoring")
root.protocol("WM_DELETE_WINDOW", exit)


def update_data():
    """
    Actualise le canvas en récupérant la figure générée par le module api_eco2mix selon la période sélectionnée par les DateEntry start_date_entry et end_date_entry ainsi que la région définie par la ComboBox combobox_region
    """
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()
    region = combobox_region.get()
    canvas = FigureCanvasTkAgg(api_eco2mix.get_monitoring_figure(start_date,end_date,region), master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0, columnspan=7, sticky="nsew")

lbl1 = tk.Label(root, text="Sélectionnez la période et la région d'analyse des données:   du")
lbl1.grid(row= 0, column= 0, padx=5, pady=5)

start_date_entry = DateEntry(root, width=12, borderwidth=2, date_pattern='dd/mm/yyyy')
start_date_entry.grid(row= 0, column= 1, padx=5, pady=5)

lbl2 = tk.Label(root, text="au")
lbl2.grid(row= 0, column= 2, padx=5, pady=5)

end_date_entry = DateEntry(root, width=12, borderwidth=2, date_pattern='dd/mm/yyyy')
end_date_entry.grid(row= 0, column= 3, padx=5, pady=5)

lbl3 = tk.Label(root, text="dans la région ")
lbl3.grid(row= 0, column= 4, padx=5, pady=5)

region_var = tk.StringVar()
regions = api_eco2mix.get_region()
combobox_region = ttk.Combobox(root, textvariable=region_var, values=api_eco2mix.get_region(), state="readonly")# utilise le module api_eco2mix pour récupérer les régions
combobox_region.current(1)
combobox_region.grid(row=0, column=5, padx=5, pady=10)


update_button = tk.Button(root, text= "Load data", command= update_data)
update_button.grid(row= 0, column= 6, padx=15, pady=5)


fig, ax = plt.subplots(figsize=(5, 4))#plot temporaire avant de faire la première requete
ax.set_title("Pas de données chargées")
ax.axis("off")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0, columnspan=7, sticky="nsew")

root.mainloop()