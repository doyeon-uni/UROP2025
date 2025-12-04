# PHREEQC_database helper
import tkinter as tk
import os
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter.messagebox import showinfo
import re
import build_database.clean_tables as ct
import build_database.utils as ut
import importlib.resources as pkg_resources


# get databases folder from build_database
database_list = pkg_resources.files('build_database.databases')
database_list = ut.phreeqc_database_list(database_list)

# create Solution Species table
solution_species = ct.compile_solution_species_table(database_list)
ss_list=list(solution_species.columns.values)

# normalizing solution species
solution_species.iloc[:,0] = solution_species.iloc[:,0].str.replace(' ', '')
ones = re.compile(r'\b1(?!\d)')
solution_species.iloc[:,0] = solution_species.iloc[:,0].str.replace(ones, '', regex=True)

# create Solution Master Species table
sms = ct.compile_master_solution_table(database_list, analysis=True)
sms_list=list(sms.columns.values)

# create phases table
phase = ct.compile_phase_table(database_list)
phase_list = list(phase.columns.values)

# function to select file
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

# function to exit the program
def quit_program():
    root.destroy()

# function to find input equation
def find_equation(equation:str):
    equation = equation.replace(" ","")
    equation = re.sub(r'\b1(?!\d)', '', equation)
    find_eq = solution_species[solution_species['equation'].str.contains(equation, regex=False)]
    return find_eq

# function to find input phases
def find_phases(phases:str):
    find_phases = phase[phase['phase_name'].str.contains(phases, regex = False)]
    return find_phases

# main class
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

        tk.Button(self, text="Edit Database", width=20, bg="#4F8FC0", fg="black",
                  activebackground="#4CAF50",
                  activeforeground="white",
                  command=lambda: master.show_frame(EditDatabasePage)).pack(pady=10)

        tk.Button(self, text="Find Values", width=20, bg="#53DEDC", fg="black",
                  activebackground="#4CAF50",
                  activeforeground="white",
                  command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)

# class that enables scrolling
class ScrollableFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, width=800, height=500)
        self.vscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.inner = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.vscrollbar.set)

# page for editing values in existing databases
class EditDatabasePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
    
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        scroll = ScrollableFrame(self)
        scroll.grid(row=0, column=0, sticky="nsew")
        inner = scroll.inner

        tk.Label(
            inner,
            text="Edit Existing Database",
            font=("DejaVu Sans Mono", 20, "bold"),
            anchor="center"
        ).pack(pady=10, fill="x")

        tk.Label(inner, text="Select Database").pack()
        self.entry_db = tk.Entry(inner, width=50)
        self.entry_db.pack()
        tk.Button(
            inner,
            text="Browse",
            command=lambda: self.browse_file(self.entry_db)
        ).pack()

        tk.Label(inner, text="New Database").pack()
        self.entry_new = tk.Entry(inner, width=50)
        self.entry_new.pack()
        tk.Button(
            inner,
            text="Browse",
            command=lambda: self.browse_save(self.entry_new)
        ).pack()

        tk.Label(inner, text="Solution Species").pack(pady=(15, 0))

        tk.Label(inner, text="Equation").pack()
        self.entry_eq = tk.Entry(inner, width=50)
        self.entry_eq.pack()

        tk.Label(inner, text="log K").pack()
        self.entry_logk = tk.Entry(inner, width=50)
        self.entry_logk.pack()

        tk.Label(inner, text="delta H (kcal/mol)").pack()
        self.entry_dh = tk.Entry(inner, width=50)
        self.entry_dh.pack()

        tk.Button(
            inner,
            text="Add/Edit Species",
            command=self.add_species,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Label(inner, text="Solution Master Species").pack(pady=(20, 0))

        tk.Label(inner, text="Element").pack()
        self.entry_sms_element = tk.Entry(inner, width=50)
        self.entry_sms_element.pack()

        tk.Label(inner, text="Master species").pack()
        self.entry_sms_species = tk.Entry(inner, width=50)
        self.entry_sms_species.pack()

        tk.Label(inner, text="Alk").pack()
        self.entry_sms_alk = tk.Entry(inner, width=50)
        self.entry_sms_alk.pack()

        tk.Label(inner, text="Element gfw").pack()
        self.entry_sms_gfw = tk.Entry(inner, width=50)
        self.entry_sms_gfw.pack()

        tk.Button(
            inner,
            text="Add/Edit Master Species",
            command=self.add_master_species,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Label(inner, text="Phase").pack(pady=(20, 0))

        tk.Label(inner, text="Phase name").pack()
        self.entry_phase_name = tk.Entry(inner, width=50)
        self.entry_phase_name.pack()

        tk.Label(inner, text="Equation").pack()
        self.entry_phase_eq = tk.Entry(inner, width=50)
        self.entry_phase_eq.pack()

        tk.Label(inner, text="log K").pack()
        self.entry_phase_logk = tk.Entry(inner, width=50)
        self.entry_phase_logk.pack()

        tk.Label(inner, text="delta H (kcal/mol)").pack()
        self.entry_phase_dh = tk.Entry(inner, width=50)
        self.entry_phase_dh.pack()

        tk.Button(
            inner,
            text="Add/Edit Phase",
            command=self.add_phase,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Button(
            inner,
            text="Back",
            command=lambda: master.show_frame(Main),
            bg="#F2DEDE"
        ).pack(pady=10)

    # find database file
    def browse_file(self, entry):
        filename = fd.askopenfilename(
            filetypes=[("Database files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    # insert the added values into the section
    def insert_into_section(self, lines, section_name, new_entry):
        start = None
        pattern = re.compile(rf'^\s*{re.escape(section_name)}\s*$', re.IGNORECASE)
        for i, line in enumerate(lines):
            if pattern.match(line):
                start = i
                break
        if start is None:
            raise ValueError(f"Section {section_name} not found.")
        end = None
        for i in range(start + 1, len(lines)):
            s = lines[i].strip()
            if not s:
                continue
            if re.match(r'^[A-Z][A-Z _]*[A-Z]$', s):
                end = i
                break
        if end is None:
            end = len(lines)
        new_lines = new_entry.splitlines(keepends=True)
        for j, nl in enumerate(new_lines):
            if not nl.endswith('\n'):
                new_lines[j] = nl + '\n'
        lines[end:end] = new_lines
        return lines
        
    # save new database file
    def browse_save(self, entry):
        filename = fd.asksaveasfilename(defaultextension=".dat")
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    # load database file based on its path
    def load_database(self, path):
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            return f.readlines()

    # write the new database
    def save_database(self, lines, path):
        with open(path, 'w') as f:
            f.writelines(lines)
    
    # normalize the equation(add spaces on either side of '=')
    def normalize_equation(self, s: str) -> str:
        if s is None:
            return ""
        s = s.strip()
        s = re.sub(r'\s*=\s*', ' = ', s)
        s = re.sub(r'\s+', ' ', s)
        return s

    # find and verify if the species already exists in the database
    def find_species(self, lines, species_eq):
        target = self.normalize_equation(species_eq)
        if not target:
            return -1
    
        for i, line in enumerate(lines):
            if self.normalize_equation(line) == target:
                return i
        return -1

    # add user input values to species
    def add_species(self):
        eq = self.normalize_equation(self.entry_eq.get().strip())
        logk = self.entry_logk.get().strip()
        dh = self.entry_dh.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not eq or not logk or not dh or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = self.load_database(db_path)
        index = self.find_species(lines, eq)

        new_entry = (
        f"    {eq}\n"
        f"    log_k {logk}\n"
        f"    delta_h {dh} kcal/mol\n\n"
        )

        new_lines = new_entry.splitlines(keepends=True)
        for j, nl in enumerate(new_lines):
            if not nl.endswith('\n'):
                new_lines[j] = nl + '\n'

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Species '{eq}' already exists.\nChange?"
            )
            if choice:
                end = index + 1
                while end < len(lines) and lines[end].strip():
                    end += 1
                del lines[index:end]
                lines.insert(index, new_entry)
                messagebox.showinfo("Edited", f"{eq} is now edited.")
            else:
                return
        else:
            self.insert_into_section(lines, "SOLUTION_SPECIES", new_entry)
            messagebox.showinfo("Added", f"{eq} is now added.")

        self.save_database(lines, new_path)

    # find and verify if the solution master species already exists in the database
    def find_master_species_line(self, lines, element_name):
        pattern = re.compile(rf'^\s*{re.escape(element_name)}\s+')
        for i, line in enumerate(lines):
            if pattern.match(line):
                return i
        return -1

    # add user input values to solution master species
    def add_master_species(self):
        element = self.entry_sms_element.get().strip()
        species = self.entry_sms_species.get().strip()
        alk = self.entry_sms_alk.get().strip()
        gfw = self.entry_sms_gfw.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not element or not species or not alk or not gfw or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = self.load_database(db_path)
        index = self.find_master_species_line(lines, element)

        new_line = f"{element}    {species}    {alk}    {gfw}\n"

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Element '{element}' already exists in SOLUTION_MASTER_SPECIES.\nChange?"
            )
            if choice:
                lines[index] = new_line
                messagebox.showinfo("Edited", f"{element} master species is now edited.")
            else:
                return
        else:
            self.insert_into_section(lines, "SOLUTION_MASTER_SPECIES", new_line)
            messagebox.showinfo("Added", f"{element} master species is now added.")

        self.save_database(lines, new_path)

    # find and verify if the phase already exists in the database
    def find_phase_line(self, lines, phase_name):
        pattern = re.compile(rf'^\s*{re.escape(phase_name)}\s*$')
        for i, line in enumerate(lines):
            if pattern.match(line):
                return i
        return -1
    
    # add user input to phase block 
    def add_phase(self):
        name = self.entry_phase_name.get().strip()
        eq = self.normalize_equation(self.entry_phase_eq.get().strip())
        logk = self.entry_phase_logk.get().strip()
        dh = self.entry_phase_dh.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not name or not eq or not logk or not dh or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = self.load_database(db_path)
        index = self.find_phase_line(lines, name)

        new_entry = (
        f"{name}\n"
        f"    {eq}\n"
        f"    log_k {logk}\n"
        f"    delta_h {dh} kcal/mol\n\n"

        )

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Phase '{name}' already exists.\nChange?"
            )
            if choice:
                end = index + 1
                while end < len(lines) and lines[end].strip():
                    end += 1
                new_lines = new_entry.splitlines(keepends=True)
                lines[index:end] = new_lines
                messagebox.showinfo("Edited", f"{name} phase is now edited.")
            else:
                return
        else:
            self.insert_into_section(lines, "PHASES", new_entry)
            messagebox.showinfo("Added", f"{name} phase is now added.")

        self.save_database(lines, new_path)


# page for finding and comparing different values
class FindValuesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Find Values", font=("DejaVu Sans Mono", 20, "bold")).pack()
        tk.Button(self, text="Find Equation", command=lambda: master.show_frame(FindEquationsPage)).pack(pady=10)
        tk.Button(self, text="Find Species", command=lambda: master.show_frame(FindSpeciesPage)).pack(pady=10)
        tk.Button(self, text="Find Phase", command=lambda: master.show_frame(FindPhasesPage)).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack()

# Finding species
class FindEquationsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_equation = tk.Entry(self, width=50)
        self.entry_equation.pack()
        tk.Button(self, text="Find Species Equation", command=self.find_and_show_equation).pack(pady=10)
        tk.Button(self, text="Export to Excel", command=self.export_to_excel).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)
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
    
    # finding and showing the browsed equations from different databases
    def find_and_show_equation(self):
        eq = self.entry_equation.get().strip()
        result_df = find_equation(eq)

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(result_df.columns)
        self.tree["show"] = "headings"

        for c in result_df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        for i, row in result_df.iterrows():
            self.tree.insert("", "end", values=list(row))  
    
    # function for exporting the result into an excel file
    def export_to_excel(self):
        sp = self.entry_equation.get().strip()
        
        if sp =="":
            messagebox.showwarning("No data", "No data entered - please enter the desired species first")
        else:
            result_df = find_species(sp)

            file_path = tk.filedialog.asksaveasfilename( defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            result_df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Data is now exported.\n\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the exportation.\n\n{e}")

# page for finding sms(solution master species)        
class FindSpeciesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_species = tk.Entry(self, width=50)
        self.entry_species.pack()
        tk.Button(self, text="Find Solution Master Species", command=self.find_and_show_species).pack(pady=10)
        tk.Button(self, text="Export to Excel", command=self.export_to_excel).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)
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
    # finding and showing sms in different database files
    def find_and_show_species(self):
        sp = self.entry_species.get().strip()
        result_df = find_species(sp)
        
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(result_df.columns)
        self.tree["show"] = "headings"
        
        for c in result_df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        for i, row in result_df.iterrows():
            self.tree.insert("", "end", values=list(row))  

    # exporting the result into an excel file
    def export_to_excel(self):
        sp = self.entry_species.get().strip()
        
        if sp =="":
            messagebox.showwarning("No data", "No data entered - please enter the desired species first")
        else:
            result_df = find_species(sp)

            file_path = tk.filedialog.asksaveasfilename( defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            result_df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Data is now exported.\n\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the exportation.\n\n{e}")

# page for finding and comparing phase values from different databases
class FindPhasesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.entry_phases = tk.Entry(self, width=50)
        self.entry_phases.pack()
        tk.Button(self, text="Find Phases", command=self.find_and_show_phases).pack(pady=10)
        tk.Button(self, text="Export to Excel", command=self.export_to_excel).pack(pady=10)
        tk.Button(self, text="Back", command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)
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

    # finding and showing phase in different databases
    def find_and_show_phases(self):
        sp = self.entry_phases.get().strip()
        result_df = find_phases(sp)
        
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(result_df.columns)
        self.tree["show"] = "headings"
        
        for c in result_df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        for i, row in result_df.iterrows():
            self.tree.insert("", "end", values=list(row))   

    # exporting found values to an excel files
    def export_to_excel(self):
        sp = self.entry_phases.get().strip()
        
        if sp =="":
            messagebox.showwarning("No data", "No data entered - please enter the desired species first")
        else:
            result_df = find_phases(sp)

            file_path = tk.filedialog.asksaveasfilename( defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            result_df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Data is now exported.\n\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the exportation.\n\n{e}")

# main app
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PHREEQC Database Helper")
        self.geometry("1000x700")

        self.frames = {}
        for F in (Main, ScrollableFrame, EditDatabasePage, FindValuesPage, FindEquationsPage, FindSpeciesPage, FindPhasesPage):
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



