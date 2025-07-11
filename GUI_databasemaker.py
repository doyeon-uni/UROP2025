# GUI Database maker
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import warnings
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import build_database.clean_tables as ct
import build_database.utils as ut
import utils
import importlib.resources as pkg_resources
import build_database.databases
# get databases folder from build_database
database_list = pkg_resources.files('build_database.databases')
database_list = ut.phreeqc_database_list(database_list)

# create Solution Species table
solution_species = ct.compile_solution_species_table(database_list)

# create Solution Master Species table
sms = ct.compile_master_solution_table(database_list, analysis=True)
# drop duplicate rows
before = len(sms)
filter_columns = ['element','species','alk','element_gfw']
sms = sms.drop_duplicates(subset=filter_columns)
after = len(sms)
before = len(solution_species)
filter_columns = solution_species.columns[:-1]
solution_species = solution_species.drop_duplicates(subset=filter_columns)
after = len(solution_species)

solution_species.iloc[:,0] = solution_species.iloc[:,0].str.replace(' ', '')
ones = re.compile(r'\b1(?!\d)')
solution_species.iloc[:,0] = solution_species.iloc[:,0].str.replace(ones, '', regex=True)

def select_files():
    filetypes = (
        ('database files', '*.dat'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes)

    showinfo(
        title='Database Selected',
        message=filenames
    )
def quit_program():
    root.destroy()

def find_equation(equation:str):
    equation = equation.replace(" ","")
    equation = re.sub(r'\b1(?!\d)', '', equation)
    find_eq = solution_species[solution_species['equation'].str.contains(equation, regex=False)]
    return find_eq

def find_species(species:str):
    find_sp = sms[sms['species'].str.contains(species, regex=False)]
    return find_sp

class Main(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label_frame = tk.Frame(self)
        label_frame.pack(fill="x")
        tk.Label(label_frame,
         text="PHREEQC Menu",
         font=("DejaVu Sans Mono", 20, "bold"),
         anchor="center",
         width=45).pack()
        tk.Button(self, text="Make Database", width=20, bg="#26648E", fg="black",
                  activebackground="#4CAF50",
                  activeforeground="white",
                  command=lambda: master.show_frame(MakeDatabasePage)).pack(pady=10)

        tk.Button(self, text="Edit Database", width=20, bg="#4F8FC0", fg="black",
                  activebackground="#4CAF50",
                  activeforeground="white",
                  command=lambda: master.show_frame(EditDatabasePage)).pack(pady=10)

        tk.Button(self, text="Find Values", width=20, bg="#53DEDC", fg="black",
                  activebackground="#4CAF50",
                  activeforeground="white",
                  command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)

class EditDatabasePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Edit Existing Database", font=("DejaVu Sans Mono", 20, "bold")).pack(pady=20)
        tk.Button(self, text="Select Database", command=select_files).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack()
        
class MakeDatabasePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Make Database (Coming Soon)", font=("DejaVu Sans Mono", 20, "bold")).pack()
        tk.Button(self, text="Select New Database Location", command=select_files).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack()

class FindValuesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Find Values (Coming Soon)", font=("DejaVu Sans Mono", 20, "bold")).pack()
        tk.Button(self, text="Find Equation", command=lambda: master.show_frame(FindEquationsPage)).pack()
        tk.Button(self, text="Find Species", command=lambda: master.show_frame(FindSpeciesPage)).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack()

class FindEquationsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_equation = tk.Entry(self, width=50)
        self.entry_equation.pack()
        tk.Button(self, text="Find Equation", command=self.find_and_show_equation).pack(pady=10)
    
        self.result_label = tk.Label(self, text="")
        self.result_label.pack()

    def find_and_show_equation(self):
        eq = self.entry_equation.get()
        result_df = find_equation(eq)
        self.result_label.config(text=str(result_df))
        
class FindSpeciesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_species = tk.Entry(self, width=50)
        self.entry_species.pack()
        tk.Button(self, text="Find Species", command=self.find_and_show_species).pack(pady=10)
    
        self.result_label = tk.Label(self, text="")
        self.result_label.pack()

    def find_and_show_species(self):
        sp = self.entry_species.get()
        result_df = find_species(sp)
        self.result_label.config(text=str(result_df))        


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PHREEQC Database Helper")
        self.geometry("750x600")

        self.frames = {}
        for F in (Main, EditDatabasePage, MakeDatabasePage, FindValuesPage, FindEquationsPage, FindSpeciesPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Main)

        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0, pady=10)
        close_button = ttk.Button(button_frame, text='Exit', command=quit_program)
        close_button.pack()

        self.show_frame(Main)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

if __name__ == "__main__":
    root = App()
    root.mainloop()
