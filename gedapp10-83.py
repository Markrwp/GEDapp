### Python3 ###
### GEDapp10-83 ###
### All working ###
### Markrwp 18/06/2025 ###
### Good on a Raspberry Pi! ###
import ged4py
import tkinter as tk
from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter.filedialog import askopenfile, askopenfilename
import sys
import os
import PIL.Image

# Corrected Pillow version compatibility check
if hasattr(PIL.Image, 'Resampling'):
    Resampling = PIL.Image.Resampling
else:
    Resampling = PIL.Image

from PIL import ImageTk
from ged4py.parser import GedcomReader
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# --- NEW CODE TO HANDLE RESOURCE PATHS ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- END NEW CODE ---


root = Tk()

# --- USE resource_path() FOR ALL IMAGE FILES ---
logo_path = resource_path('logo-3.png')
logo = PIL.Image.open(logo_path)
logo = logo.resize((115,115), Resampling.LANCZOS)
logo = ImageTk.PhotoImage(logo)

picture1_path = resource_path('candlelit_parchment.jpg')
picture1 = PIL.Image.open(picture1_path)
picture1 = picture1.resize((145,145), Resampling.LANCZOS)
picture1 = ImageTk.PhotoImage(picture1)

picture2_path = resource_path('Tree_mag_glass.jpg')
picture2 = PIL.Image.open(picture2_path)
picture2 = picture2.resize((145,145), Resampling.LANCZOS)
picture2 = ImageTk.PhotoImage(picture2)
# --- END MODIFIED IMAGE LOADING ---

def displayResults(parent, input_box, text_box):
    # Ensure the parent window is active before opening the file dialog
    parent.lift()
    parent.focus_force()
    file = askopenfile(parent=parent, mode='rb', title="Choose a file", \
    filetypes=[("GEDCOM file", "*.GED"),("GEDCOM file", "*.ged"),("csv file","*.csv")])
    if file:
        parser = GedcomReader(file)
        page_content = ''
        found_individual = False # Flag to track if any individual is found

        for i, indi in enumerate(parser.records0("INDI")):
            name = indi.name

            if name:
                if input_box:
                    if name.format() != input_box.get():
                        continue
                        
                found_individual = True 

                page_content += f"\n{i}:\n"
                page_content += f"    Name: {indi.name.format()}\n"

                father = indi.father
                if father:
                    page_content += f"    Father: {father.name.format()}\n"

                mother = indi.mother
                if mother:
                    page_content += f"    Mother: {mother.name.format()}\n"

                birth_date = indi.sub_tag_value("BIRT/DATE")
                if birth_date:
                    page_content += f"    Birth date: {birth_date}\n"

                birth_place = indi.sub_tag_value("BIRT/PLAC")
                if birth_place:
                    page_content += f"    Birth place: {birth_place}\n"

                death_date = indi.sub_tag_value("DEAT/DATE")
                if death_date:
                    page_content += f"    Death date: {death_date}\n"

                death_place = indi.sub_tag_value("DEAT/PLAC")
                if death_place:
                    page_content += f"    Death place: {death_place}\n"
                    
                occupation = indi.sub_tag_value("OCCU")
                if occupation:
                    page_content += f"    Occupation: {occupation}\n"
                    
                fams_links = indi.sub_tags('FAMS')

                found_spouses = False
                for fam_link in fams_links:
                    family = fam_link
                    if family:
                        spouses_links1 = family.sub_tags('HUSB')
                        for spouse_link1 in spouses_links1:
                            husband = spouse_link1
                            if husband:
                                page_content += f"\nHusband: {husband.name.format()} (ID: {husband.xref_id})\n"

                        spouses_links2 = family.sub_tags('WIFE')
                        for spouse_link2 in spouses_links2:
                            wife = spouse_link2
                            if wife:
                                page_content += f"Wife: {wife.name.format()} (ID: {wife.xref_id})\n"

                        marr_dates = family.sub_tags('MARR/DATE')
                        for marr_date in marr_dates:
                            date = marr_date
                            if marr_date:
                                page_content += f"Marriage Date: {marr_date.value}\n\n"

                        marr_places = family.sub_tags('MARR/PLAC')
                        for marr_place in marr_places:
                            place = marr_place
                            if marr_place:
                                page_content += f"Marriage Place: {marr_place.value}\n\n"
                                found_spouses = True

                    else:
                        page_content += f"\nCould not find family for FAMS link: {fam_link.value}\n"

                if not found_spouses:
                    page_content += f"\nNo record of marriage found for this individual.\n"

                found_children = False
                for fam_link in fams_links:
                    family = fam_link
                    if family:
                        children_links = family.sub_tags('CHIL')
                        for child_link in children_links:
                            child = child_link
                            if child:
                                page_content += f" Child: {child.name.format()} (ID: {child.xref_id})\n"
                                found_children = True
                    else:
                        page_content += f"\nCould not find family for FAMS link: {fam_link.value}\n"

                if not found_children:
                    page_content += "\nNo children found for this individual.\n"
                                
                note = indi.sub_tag_value("NOTE")
                if note:
                    page_content += f"\n NOTES: {note}\n"

                xref = indi.xref_id
                if xref:
                    page_content += f"    Reference ID: {indi.xref_id}\n"

        if input_box and not found_individual:
            page_content = "\nNo individual by this name in this .ged file.\n" \
            "\nDid you enter the individual's full name in the search box?\n" \
            "\nDid you enter the surname in the correct case format?\n" \
            "\nCheck spelling!\n"

        text_box.insert(1.0, page_content)
        text_box.tag_configure("center", justify="center")
        text_box.tag_add("center", 1.0, "end")


def browseGED():
    top = Toplevel(root)
    top.title("Browse GED file")
    top.geometry("1020x500")
    top.columnconfigure(0, weight=1)
    top.rowconfigure(0, weight=1)
    # Changed background color to parchment
    text_box = scrolledtext.ScrolledText(top, font="Courier 12", padx=15, pady=15, bg="#FDF5E6") 
    text_box.grid(column=0, row=0, sticky=E+W+N+S)
    displayResults(top, None, text_box)
    

def browseCSV():
    import pandastable as pt
    from pandastable import Table

    try:
        # Use 'parent' argument for filedialog to associate it with the root window
        file = filedialog.askopenfilename(parent=root, filetypes=[('CSV files', "*.csv"), ('All', "*.*")])
        if file:
            df = pd.read_csv(file)
            top = Toplevel(root)
            top.title('CSV Data')
            frame = tk.Frame(top)
            frame.pack(fill='both', expand=True)
            table = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
            table.show()
    except FileNotFoundError:
        tk.messagebox.showerror("Error", "CSV file not found.")
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error reading CSV file: {e}")        

def searchGED():
    top = Toplevel(root)
    top.title("Search GED file")
    top.geometry("1020x500")
    top.columnconfigure(0, weight=1)
    top.rowconfigure(2, weight=1)
    top.configure(bg="DarkSeaGreen1")

    input_frame = Frame(top)
    input_frame.grid(row=0, column=0, sticky=E+W+N+S)
    input_frame.columnconfigure(1, weight=1)
    input_frame.configure(bg="DarkSeaGreen1")

    label = Label(input_frame, text="Enter Full Birth Name as found in a .GED file,\nrespecting the case format:", font="Raleway 10 bold", bg="DarkSeaGreen1")
    label.grid(column=1, row=1, padx=1, pady=5)
    
    input_box = Entry(input_frame, width=30, font="Raleway 10", justify="center")
    input_box.grid(column=1, row=2, padx=5, pady=5)

    text_frame = Frame(top)
    text_frame.grid(column=0, row=2, columnspan=4, padx=20, pady=5, sticky=E+W+N+S)

    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    # Changed background color to parchment
    text_box = scrolledtext.ScrolledText(text_frame, font="Courier 12", padx=10, pady=2, bg="#FDF5E6") 
    text_box.grid(column=0, row=0, sticky=E+W+N+S)
    
    button = Button(input_frame, text='Search a .GED for Individual(s)', font="Raleway 10", bg=("yellow"), command=lambda:displayResults(text_frame, input_box, text_box))
    button.grid(column=0, row=2, padx=20, pady=10)
    
    button = Button(input_frame, text='Save results to clipboard', font="Raleway 10", bg=("RoyalBlue1"), command=lambda:gtc(text_box.get(1.0, "end-1c")))
    button.grid(column=2, row=2, padx=20, pady=10)
    
    logo_label = Label(input_frame, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0, padx=5, pady=10)

def gtc(dtxt):
    root.clipboard_clear()
    root.clipboard_append(dtxt)

###New from 10-80 - Graph of family birthplaces###
def plot_birthplaces_for_surname(surname_to_find):
    if not surname_to_find:
        tk.messagebox.showwarning("Input Error", "Please enter a surname to plot.")
        return

    # Prompt user to select a GEDCOM file
    file_path = filedialog.askopenfilename(parent=root, title="Choose a GEDCOM file", filetypes=[("GEDCOM files", "*.GED *.ged")])
    if not file_path:
        tk.messagebox.showwarning("File Error", "No GEDCOM file selected to plot.")
        return

    birthplace_counts = {}

    try:
        with GedcomReader(file_path) as parser:
            for indi in parser.records0("INDI"):
                name_obj = indi.name
                if name_obj and hasattr(name_obj, 'surname') and name_obj.surname and name_obj.surname.lower() == surname_to_find.lower():
                    birth_place = indi.sub_tag_value("BIRT/PLAC")
                    if birth_place:
                        # Normalize place names for better grouping (e.g., remove extra spaces, standardizing case)
                        normalized_place = birth_place.strip().title()
                        birthplace_counts[normalized_place] = birthplace_counts.get(normalized_place, 0) + 1
        
        if not birthplace_counts:
            tk.messagebox.showinfo("No Data", f"No birthplaces found for individuals with surname '{surname_to_find}'.")
            return

        # Sort the birthplaces for consistent plotting
        sorted_places = sorted(birthplace_counts.items(), key=lambda item: item[1], reverse=True)
        places = [item[0] for item in sorted_places]
        counts = [item[1] for item in sorted_places]

        # Create a new Toplevel window for the plot
        plot_window = Toplevel(root)
        # setting font size to 8
        # plt.rcParams.update({'font.size': 8})
        plot_window.title(f"Birthplaces for Surname: {surname_to_find}")
        plot_window.geometry("800x580")
        plot_window.grab_set() # Make the plot window modal

        fig, ax = plt.subplots(figsize=(13.75, 5.25))
        ax.bar(places, counts, color='skyblue')
        ax.set_xlabel("Birthplace", labelpad=1, fontsize=11)
        ax.set_ylabel("Number of Births", labelpad=1, fontsize=11)
        ax.set_title(f"Number of Births by Place for Surname: {surname_to_find}", fontsize=12)
        # Adjust the font size of the x-tick labels
        ax.tick_params(axis='x', labelsize=7) # Adjust labelsize as needed
        # Adjust the left margin (as a fraction of the figure width)
        # Increase 'left' to push the plot area to the right, making space for the y-label
        plt.subplots_adjust(left=0.7, bottom=0.1) # You might need to experiment with this value
        
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.update()
        canvas_widget.pack(side=TOP, fill=BOTH, expand=1)

    except Exception as e:
        tk.messagebox.showerror("Error", f"Error generating plot: {e}")


def find_births_by_place():
    top1 = Toplevel(root)
    top1.title("Find Individuals Born in a Place")
    top1.geometry("1020x500")
    top1.columnconfigure(0, weight=1)
    top1.rowconfigure(2, weight=1)
    top1.configure(bg="DarkSeaGreen1")

    # Make this Toplevel window transient for the root window
    top1.transient(root)  
    # Make this Toplevel window modal, grabbing all input events
    top1.grab_set()
    
    input_frame1 = Frame(top1, bg="DarkSeaGreen1")
    input_frame1.grid(row=0, column=0, sticky=E+W+N+S)
    input_frame1.columnconfigure(1, weight=1)

    label1 = Label(input_frame1, text="Enter the birth place to search for:\n(e.g., London, Middlesex, England)", font="Raleway 10 bold", bg="DarkSeaGreen1")
    label1.grid(column=1, row=1, padx=1, pady=5)
    
    place_input1 = Entry(input_frame1, width=40, font="Raleway 10", justify="center")
    place_input1.grid(column=1, row=2, padx=5, pady=5)

    def search_birthplace_in_gedcom():
        place_to_find = place_input1.get().strip()
        if not place_to_find:
            tk.messagebox.showwarning("Input Error", "Please enter a place name to search.")
            # Ensure the window is on top even if no file dialog opens
            top1.lift() # Lift the Toplevel window
            top1.focus_force() # Force focus back to the Toplevel window
            return

        # Pass 'parent=top1' to filedialog to ensure it stays on top of the Toplevel
        file_path = filedialog.askopenfilename(parent=top1, title="Choose a GEDCOM file", filetypes=[("GEDCOM files", "*.GED *.ged")])
        
        # After the file dialog closes, explicitly lift and focus the modal window
        top1.lift()
        top1.focus_force()

        if not file_path:
            return # User cancelled file dialog

        text_box1.delete(1.0, END)  
        birth_place_count = 0
        individuals_found = []

        try:
            with GedcomReader(file_path) as parser:
                for indi in parser.records0("INDI"):
                    birth_place = indi.sub_tag_value("BIRT/PLAC")
                    if birth_place and place_to_find.lower() in birth_place.lower():
                        birth_place_count += 1
                        individuals_found.append(indi.name.format())
            
            if birth_place_count > 0:
                result_text = f"\nFound {birth_place_count} individual(s) who were born in '{place_to_find}' or a sub-place:\n\n"
                for name in individuals_found:
                    result_text += f"- {name}\n"
            else:
                result_text = f"\nNo individual(s) found who were born in '{place_to_find}'.\n"

            text_box1.insert(1.0, result_text)
            text_box1.tag_configure("center", justify="center")
            text_box1.tag_add("center", 1.0, "end")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading GEDCOM file: {e}")

    text_frame1 = Frame(top1)
    text_frame1.grid(column=0, row=2, columnspan=4, padx=20, pady=5, sticky=E+W+N+S)
    text_frame1.rowconfigure(0, weight=1)
    text_frame1.columnconfigure(0, weight=1)

    # Changed background color to parchment
    text_box1 = scrolledtext.ScrolledText(text_frame1, font="Courier 12", padx=10, pady=2, bg="#FDF5E6") 
    text_box1.grid(column=0, row=0, sticky=E+W+N+S)

    search_button = Button(input_frame1, text='Choose a .GED to examine', font="Raleway 10", bg="yellow", command=search_birthplace_in_gedcom)
    search_button.grid(column=0, row=2, padx=20, pady=10)
    
    clipboard_button = Button(input_frame1, text='Save results to clipboard', font="Raleway 10", bg="RoyalBlue1", command=lambda:gtc(text_box1.get(1.0, "end-1c")))
    clipboard_button.grid(column=2, row=2, padx=20, pady=10)

    logo_label = Label(input_frame1, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0, padx=5, pady=10)
    # This line will pause the main application until 'top' is closed
    root.wait_window(top1)
###End of new in 10-65###
    
###New in 10-66###
def find_marriages_by_place():
    top = Toplevel(root)
    top.title("Find Individuals who Married in a Place")
    top.geometry("1020x500")
    top.columnconfigure(0, weight=1)
    top.rowconfigure(2, weight=1)
    top.configure(bg="DarkSeaGreen1")

    # Make this Toplevel window transient for the root window
    top.transient(root)  
    # Make this Toplevel window modal, grabbing all input events
    top.grab_set()
    
    input_frame = Frame(top, bg="DarkSeaGreen1")
    input_frame.grid(row=0, column=0, sticky=E+W+N+S)
    input_frame.columnconfigure(1, weight=1)

    label = Label(input_frame, text="Enter the marriage place to search for:\n(e.g., London, Middlesex, England)", font="Raleway 10 bold", bg="DarkSeaGreen1")
    label.grid(column=1, row=1, padx=1, pady=5)
    
    place_input = Entry(input_frame, width=40, font="Raleway 10", justify="center")
    place_input.grid(column=1, row=2, padx=5, pady=5)

    text_frame = Frame(top)
    text_frame.grid(column=0, row=2, columnspan=4, padx=20, pady=5, sticky=E+W+N+S)
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    # Changed background color to parchment
    text_box = scrolledtext.ScrolledText(text_frame, font="Courier 12", padx=10, pady=2, bg="#FDF5E6") 
    text_box.grid(column=0, row=0, sticky=E+W+N+S)

    def search_marrplace_in_gedcom():
        place_to_find = place_input.get().strip()
        if not place_to_find:
            tk.messagebox.showwarning("Input Error", "Please enter a place name to search.")
            # Ensure the window is on top even if no file dialog opens
            top.lift()
            top.focus_force()
            return

        # Pass 'parent=top' to filedialog to ensure it stays on top of the Toplevel
        file_path = filedialog.askopenfilename(parent=top, title="Choose a GEDCOM file", filetypes=[("GEDCOM files", "*.GED *.ged")])
        
        # After the file dialog closes, explicitly lift and focus the modal window
        top.lift()
        top.focus_force()

        if not file_path:
            return # User cancelled file dialog

        text_box.delete(1.0, END)  
        marr_place_count = 0
        individuals_found = []

        try:
            with GedcomReader(file_path) as parser:
                for indi in parser.records0("INDI"):
                    # Iterate through FAMS links to find marriage places
                    marr_place = indi.sub_tag_value("FAMS/MARR/PLAC")
                    if marr_place and place_to_find.lower() in marr_place.lower():
                        marr_place_count += 1
                        individuals_found.append(indi.name.format())
            
            if marr_place_count > 0:
                result_text = f"\nFound {marr_place_count} individual(s) who married in '{place_to_find}' or a sub-place:\n\n"
                # Remove duplicates from individuals_found
                individuals_found = sorted(list(set(individuals_found)))
                for name in individuals_found:
                    result_text += f"- {name}\n"
            else:
                result_text = f"\nNo individual(s) found who married in '{place_to_find}'.\n"

            text_box.insert(1.0, result_text)
            text_box.tag_configure("center", justify="center")
            text_box.tag_add("center", 1.0, "end")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading GEDCOM file: {e}")

    search_button = Button(input_frame, text='Choose a .GED to examine', font="Raleway 10", bg="yellow", command=search_marrplace_in_gedcom)
    search_button.grid(column=0, row=2, padx=20, pady=10)
    
    clipboard_button = Button(input_frame, text='Save results to clipboard', font="Raleway 10", bg="RoyalBlue1", command=lambda:gtc(text_box.get(1.0, "end-1c")))
    clipboard_button.grid(column=2, row=2, padx=20, pady=10)

    logo_label = Label(input_frame, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0, padx=5, pady=10)

    # This line will pause the main application until 'top' is closed
    root.wait_window(top)

###End of Marriages by Place###

def find_deaths_by_place():
    top = Toplevel(root)
    top.title("Find Individuals who Died in a Place")
    top.geometry("1020x500")
    top.columnconfigure(0, weight=1)
    top.rowconfigure(2, weight=1)
    top.configure(bg="DarkSeaGreen1")

    # Make this Toplevel window transient for the root window
    top.transient(root)  
    # Make this Toplevel window modal, grabbing all input events
    top.grab_set()
    
    input_frame = Frame(top, bg="DarkSeaGreen1")
    input_frame.grid(row=0, column=0, sticky=E+W+N+S)
    input_frame.columnconfigure(1, weight=1)

    label = Label(input_frame, text="Enter the death place to search for:\n(e.g., London, Middlesex, England)", font="Raleway 10 bold", bg="DarkSeaGreen1")
    label.grid(column=1, row=1, padx=1, pady=5)
    
    place_input = Entry(input_frame, width=40, font="Raleway 10", justify="center")
    place_input.grid(column=1, row=2, padx=5, pady=5)

    text_frame = Frame(top)
    text_frame.grid(column=0, row=2, columnspan=4, padx=20, pady=5, sticky=E+W+N+S)
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    # Changed background color to parchment
    text_box = scrolledtext.ScrolledText(text_frame, font="Courier 10", padx=10, pady=2, bg="#FDF5E6") 
    text_box.grid(column=0, row=0, sticky=E+W+N+S)

    def search_deathplace_in_gedcom():
        place_to_find = place_input.get().strip()
        if not place_to_find:
            tk.messagebox.showwarning("Input Error", "Please enter a place name to search.")
            # Ensure the window is on top even if no file dialog opens
            top.lift()
            top.focus_force()
            return

        # Pass 'parent=top' to filedialog to ensure it stays on top of the Toplevel
        file_path = filedialog.askopenfilename(parent=top, title="Choose a GEDCOM file", filetypes=[("GEDCOM files", "*.GED *.ged")])
        
        # After the file dialog closes, explicitly lift and focus the modal window
        top.lift()
        top.focus_force()

        if not file_path:
            return # User cancelled file dialog

        text_box.delete(1.0, END)  
        death_place_count = 0
        individuals_found = []

        try:
            with GedcomReader(file_path) as parser:
                for indi in parser.records0("INDI"):
                    death_place = indi.sub_tag_value("DEAT/PLAC")
                    if death_place and place_to_find.lower() in death_place.lower():
                        death_place_count += 1
                        individuals_found.append(indi.name.format())
            
            if death_place_count > 0:
                result_text = f"\nFound {death_place_count} individual(s) who died in '{place_to_find}' or a sub-place:\n\n"
                for name in individuals_found:
                    result_text += f"- {name}\n"
            else:
                result_text = f"\nNo individual(s) found who died in '{place_to_find}'.\n"

            text_box.insert(1.0, result_text)
            text_box.tag_configure("center", justify="center")
            text_box.tag_add("center", 1.0, "end")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading GEDCOM file: {e}")

    search_button = Button(input_frame, text='Choose a .GED to examine', font="Raleway 10", bg="yellow", command=search_deathplace_in_gedcom)
    search_button.grid(column=0, row=2, padx=20, pady=10)
    
    clipboard_button = Button(input_frame, text='Save results to clipboard', font="Raleway 10", bg="RoyalBlue1", command=lambda:gtc(text_box.get(1.0, "end-1c")))
    clipboard_button.grid(column=2, row=2, padx=20, pady=10)

    logo_label = Label(input_frame, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0, padx=5, pady=10)

    # This line will pause the main application until 'top' is closed
    root.wait_window(top)

###End of Deaths by Place###

def calculate_average_death_age():
    top = Toplevel(root)
    top.title("Calculate Average Age of Death by Surname")
    top.geometry("1020x500")
    top.columnconfigure(0, weight=1)
    top.rowconfigure(2, weight=1)
    top.configure(bg="DarkSeaGreen1")

    top.transient(root)
    top.grab_set()

    input_frame = Frame(top, bg="DarkSeaGreen1")
    input_frame.grid(row=0, column=0, sticky=E+W+N+S)
    input_frame.columnconfigure(1, weight=1)

    label = Label(input_frame, text="Enter the surname to calculate average death age for:\n(e.g., Smith)", font="Raleway 10 bold", bg="DarkSeaGreen1")
    label.grid(column=1, row=1, padx=1, pady=5)
    
    surname_input = Entry(input_frame, width=40, font="Raleway 10", justify="center")
    surname_input.grid(column=1, row=2, padx=5, pady=5)

    text_frame = Frame(top)
    text_frame.grid(column=0, row=2, columnspan=4, padx=20, pady=5, sticky=E+W+N+S)
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    # Changed background color to parchment
    text_box = scrolledtext.ScrolledText(text_frame, font="Courier 14", padx=10, pady=2, bg="#FDF5E6") 
    text_box.grid(column=0, row=0, sticky=E+W+N+S)

    def search_and_calculate():
        surname_to_find = surname_input.get().strip()
        if not surname_to_find:
            tk.messagebox.showwarning("Input Error", "Please enter a surname to search for.")
            top.lift()
            top.focus_force()
            return

        # Pass 'parent=top' to filedialog to ensure it stays on top of the Toplevel
        file_path = filedialog.askopenfilename(parent=top, title="Choose a GEDCOM file", filetypes=[("GEDCOM files", "*.GED *.ged")])
        
        top.lift()
        top.focus_force()

        if not file_path:
            return

        text_box.delete(1.0, END)
        ages_of_death = []

        try:
            with GedcomReader(file_path) as parser:
                for indi in parser.records0("INDI"):
                    name_obj = indi.name
                    if name_obj and hasattr(name_obj, 'surname') and name_obj.surname and name_obj.surname.lower() == surname_to_find.lower():
                        birth_date_data = indi.sub_tag_value("BIRT/DATE")
                        death_date_data = indi.sub_tag_value("DEAT/DATE")

                        birth_date_str = None
                        death_date_str = None

                        if birth_date_data is not None:
                            if hasattr(birth_date_data, 'value'):
                                birth_date_str = birth_date_data.value
                            else:
                                # Fallback if for some reason it's an object without .value, try direct str conversion
                                birth_date_str = str(birth_date_data) 

                        if death_date_data is not None:
                            if hasattr(death_date_data, 'value'):
                                death_date_str = death_date_data.value
                            else:
                                # Fallback if for some reason it's an object without .value, try direct str conversion
                                death_date_str = str(death_date_data)

                        if birth_date_str and death_date_str:
                            try:
                                # Attempt to parse full date first
                                birth_date = datetime.strptime(birth_date_str, "%d %b %Y")
                                death_date = datetime.strptime(death_date_str, "%d %b %Y")
                            except ValueError:
                                try:
                                    # If full date fails, try year only
                                    birth_date = datetime.strptime(birth_date_str, "%Y")
                                    death_date = datetime.strptime(death_date_str, "%Y")
                                except ValueError:
                                    continue # Cannot parse dates, skip this individual
                            
                            age_in_days = (death_date - birth_date).days
                            age_in_years = age_in_days / 365.25 # Account for leap years
                            ages_of_death.append(age_in_years)

            if ages_of_death:
                average_age = sum(ages_of_death) / len(ages_of_death)
                result_text = f"\nFor surname '{surname_to_find}':\n\n"
                result_text += f"Number of individuals with birth and death dates: {len(ages_of_death)}\n"
                result_text += f"Average age of death: {average_age:.2f} years\n"
            else:
                result_text = f"\nNo individuals with surname '{surname_to_find}' found with both birth and death dates.\n"

            text_box.insert(1.0, result_text)
            text_box.tag_configure("center", justify="center")
            text_box.tag_add("center", 1.0, "end")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading GEDCOM file: {e}")

    search_button = Button(input_frame, text='Choose a .GED to examine', font="Raleway 10", bg="yellow", command=search_and_calculate)
    search_button.grid(column=0, row=2, padx=20, pady=10)
    
    clipboard_button = Button(input_frame, text='Save results to clipboard', font="Raleway 10", bg="RoyalBlue1", command=lambda:gtc(text_box.get(1.0, "end-1c")))
    clipboard_button.grid(column=2, row=2, padx=20, pady=10)

    logo_label = Label(input_frame, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0, padx=5, pady=10)

    root.wait_window(top)

def mainWindow():
    root.title("GEDapp")

    root.resizable(True, True)

    root.geometry("1020x520")
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.configure(bg="DarkSeaGreen1")

    shadow1 = Label(root, text="Welcome to GEDapp!\n- Find, save & print data from local .GED files", font="Raleway 10 bold", bg="burlywood", padx=13, pady=9)
    shadow1.grid(column=1, row=1)
    
    title = Label(root, text="Welcome to GEDapp!\n- Find, save & print data from local .GED files", font="Raleway 10 bold", bg="navajowhite2", padx=10, pady=6)
    title.grid(column=1, row=1)

    logo_label = Label(root, image=logo, borderwidth=3, relief="raised", bg="burlywood")
    logo_label.grid(column=1, row=0)

    picture1_label = Label(root, image=picture1, borderwidth=3, relief="raised", bg="burlywood")
    picture1_label.grid(column=0, row=0, padx=5, pady=7)

    picture2_label = Label(root, image=picture2, borderwidth=3, relief="raised", bg="burlywood")
    picture2_label.grid(column=2, row=0, padx=5, pady=7)

    instructions = Label(root, text="Open a local .GED file\nto view its text", font="Raleway 10", bg="DarkSeaGreen1")
    instructions.grid(column=0, row=2, padx=20, pady=2)

    instructions1 = Label(root, text="Select a name from a .GED file\nto view an individual's records", font="Raleway 10", bg="DarkSeaGreen1")
    instructions1.grid(column=1, row=2, padx=20, pady=2)
    
    instructions2 = Label(root, text="Choose a local .CSV file\nto view data", font="Raleway 10", bg="DarkSeaGreen1")
    instructions2.grid(column=2, row=2, padx=20, pady=2)

    instructions3 = Label(root, text="Choose a local .GED file\nto find births in a place", font="Raleway 10", bg="DarkSeaGreen1")
    instructions3.grid(column=0, row=4, padx=20, pady=3)

    instructions4 = Label(root, text="Choose a local .GED file\nto find marriages in a place", font="Raleway 10", bg="DarkSeaGreen1")
    instructions4.grid(column=1, row=4, padx=20, pady=3)
    
    instructions5 = Label(root, text="Choose a local .GED file\nto find deaths in a place", font="Raleway 10", bg="DarkSeaGreen1")
    instructions5.grid(column=2, row=4, padx=20, pady=3)

    instructions6 = Label(root, text="Calculate average death age by surname", font="Raleway 10", bg="DarkSeaGreen1")
    instructions6.grid(column=1, row=6, padx=20, pady=1)
    
    # New label and entry for surname on the main window
    instructions7 = Label(root, text="Enter Surname for Graph of Births:", font="Raleway 10", bg="DarkSeaGreen1")
    instructions7.grid(column=0, row=6, padx=20, pady=1)
    
    surname_for_plot_input = Entry(root, width=20, font="Raleway 10", justify="center")
    surname_for_plot_input.grid(column=0, row=7, padx=5, pady=1)


    copyright = Label(root, text="Copyright © : Mark W-P  21-06-2025", font="Courier 6",bg="DarkSeaGreen1")
    copyright.grid(column=1,row=8)   
 
    browse = Button(root, text='Open', font="Raleway 11", bg="yellow", command=browseGED)
    browse.grid(column=0, row=3, padx=5, pady=2)
    
    select = Button(root, text='Select', font="Raleway 11", bg="RoyalBlue1", command=searchGED)
    select.grid(column=1, row=3, padx=5, pady=2)
    
    browse2 = Button(root, text='Browse', font="Raleway 11", bg="orange red", command=browseCSV)
    browse2.grid(column=2, row=3, padx=5, pady=2)

    browse3 = Button(root, text='Browse', font="Raleway 11", bg="salmon", command=find_births_by_place)
    browse3.grid(column=0, row=5, padx=5, pady=2)

    browse4 = Button(root, text='Browse', font="Raleway 11", bg="chartreuse1", command=find_marriages_by_place)
    browse4.grid(column=1, row=5, padx=5, pady=2)
    
    browse5 = Button(root, text='Browse', font="Raleway 11", bg="gray82", command=find_deaths_by_place)
    browse5.grid(column=2, row=5, padx=5, pady=2)

    avg_age_button = Button(root, text='Calculate', font="Raleway 11", bg="orange", command=calculate_average_death_age)
    avg_age_button.grid(column=1, row=7, padx=5, pady=2) # Adjusted row for consistency

    # New Plot on Graph button, now referencing the new surname input
    plot_button = Button(root, text='Graph Births', font="Raleway 11", bg="mediumpurple", command=lambda: plot_birthplaces_for_surname(surname_for_plot_input.get().strip()))
    plot_button.grid(column=0, row=8, padx=5, pady=2) # Adjusted row for consistency


    root.mainloop()

if __name__ == "__main__":
    mainWindow()

