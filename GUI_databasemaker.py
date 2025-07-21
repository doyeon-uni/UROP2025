# GUI Database maker
import tkinter as tk
import os
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import tkinter.messagebox
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
ss_list=list(solution_species.columns.values)

# create Solution Master Species table
sms = ct.compile_master_solution_table(database_list, analysis=True)
sms_list=list(sms.columns.values)
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
         width=60).pack()
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
        """
        tk.Label(self, text="Edit Existing Database", font=("DejaVu Sans Mono", 20, "bold")).pack(pady=20)
        tk.Button(self, text="Select Database", command=select_files).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack()
        """

        tk.Label(self, text="Edit Existing Database", font=("DejaVu Sans Mono", 20, "bold")).pack(pady=10)

        tk.Label(self, text="Select Database").pack()
        self.entry_db = tk.Entry(self, width=50)
        self.entry_db.pack()
        tk.Button(self, text="Browse", command=lambda: self.browse_file(self.entry_db)).pack()

        tk.Label(self, text="New Database").pack()
        self.entry_new = tk.Entry(self, width=50)
        self.entry_new.pack()
        tk.Button(self, text="Browse", command=lambda: self.browse_save(self.entry_new)).pack()

        tk.Label(self, text="Species").pack()
        self.entry_species = tk.Entry(self, width=50)
        self.entry_species.pack()

        tk.Label(self, text="Equation").pack()
        self.entry_eq = tk.Entry(self, width=50)
        self.entry_eq.pack()

        tk.Label(self, text="log K").pack()
        self.entry_logk = tk.Entry(self, width=50)
        self.entry_logk.pack()

        tk.Label(self, text="delta H (kcal/mol)").pack()
        self.entry_dh = tk.Entry(self, width=50)
        self.entry_dh.pack()

        tk.Button(self, text="Add/Edit", command=self.add_species, bg="#DFF0D8").pack(pady=5)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main), bg="#F2DEDE").pack()

    def browse_file(self, entry):
        filename = fd.askopenfilename(filetypes=[("Database files", "*.dat"), ("All files", "*.*")])
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def browse_save(self, entry):
        filename = fd.asksaveasfilename(defaultextension=".dat")
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def load_database(self, path):
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            return f.readlines()

    def save_database(self, lines, path):
        with open(path, 'w') as f:
            f.writelines(lines)

    def find_species(self, lines, species_name):
        pattern = re.compile(rf'^{re.escape(species_name)}\s+')
        for i, line in enumerate(lines):
            if pattern.match(line):
                return i
        return -1

    def add_species(self):
        species = self.entry_species.get().strip()
        eq = self.entry_eq.get().strip()
        logk = self.entry_logk.get().strip()
        dh = self.entry_dh.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not species or not eq or not logk or not dh or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = self.load_database(db_path)
        index = self.find_species(lines, species)

        new_entry = f"{eq}\n        log_k     {logk}\n        delta_h   {dh} kcal/mol\n\n"

        if index != -1:
            choice = messagebox.askyesno("Duplicate found", f"Species '{species}'already exists.\nChange?")
            if choice:
                end = index + 1
                while end < len(lines) and lines[end].strip():
                    end += 1
                del lines[index:end]
                lines.insert(index, new_entry)
                messagebox.showinfo("수정 완료", f"{species} 항목이 수정되었습니다.")
            else:
                return
        else:
            lines.append(new_entry)
            messagebox.showinfo("추가 완료", f"{species} 항목이 새로 추가되었습니다.")

        self.save_database(lines, new_path)

        
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
        tk.Button(self, text="Back", command=lambda: master.show_frame(FindValuesPage)).pack()
        self.tree_frame = tk.Frame(self, width=800, height=500)
        self.tree_frame.pack_propagate(False)
        self.tree_frame.pack()
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill='both', expand=True)
        yscroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        yscroll.pack(side='right', fill='y')
        xscroll = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.tree.xview)
        xscroll.pack(side='bottom',fill='x')
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    

    def find_and_show_equation(self):
        eq = self.entry_equation.get()
        result_df = find_equation(eq)

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(result_df.columns)
        self.tree["show"] = "headings"

        for c in result_df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        for i, row in result_df.iterrows():
            self.tree.insert("", "end", values=list(row))  
        
class FindSpeciesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_species = tk.Entry(self, width=50)
        self.entry_species.pack()
        tk.Button(self, text="Find Species", command=self.find_and_show_species).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(FindValuesPage)).pack()
        self.tree_frame = tk.Frame(self, width=800, height=500)
        self.tree_frame.pack_propagate(False)
        self.tree_frame.pack()
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill='both', expand=True)
        yscroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        yscroll.pack(side='right', fill='y')
        xscroll = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.tree.xview)
        xscroll.pack(side='bottom',fill='x')
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    def find_and_show_species(self):
        sp = self.entry_species.get()
        result_df = find_species(sp)
        
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(result_df.columns)
        self.tree["show"] = "headings"
        
        for c in result_df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        for i, row in result_df.iterrows():
            self.tree.insert("", "end", values=list(row))      


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PHREEQC Database Helper")
        self.geometry("1000x700")

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
