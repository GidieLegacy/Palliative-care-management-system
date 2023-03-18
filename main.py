import os
import tkinter as tk
import uuid
from tkinter import *
from tkinter import ttk, messagebox, filedialog

from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import mysql.connector
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.platypus import SimpleDocTemplate

path1 = os.path.normpath("C:/Users/Gideon Kiprotich/Downloads/icon-pharm.png")
path2 = os.path.normpath("C:/Users/Gideon Kiprotich/Downloads/pallaitive.jpg")
path3 = os.path.normpath("C:/Users/Gideon Kiprotich/Downloads/palliative.jpg")

# Create MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Legacy@96",
    database="pms_db"
)

# Create cursor
mycursor = mydb.cursor()


class PalliativeCare:

    def __init__(self, root):
        self.root = root
        self.root.title("Palliative Care Management System")
        self.root.geometry("1350x800+0+0")

        """"Clear all fields"""

        def clear():
            # Clear the fields
            entPatientID.delete(0, END)
            entPatientName.delete(0, END)
            entPatientAge.delete(0, END)
            gender_combo.current(0)
            entPatientDiagnosis.delete(0, END)
            txtPatientWard.delete(0, END)
            txtPatientProgressNotes.delete(0, END)

            txtPatientConstituency.delete("1.0", END)

            """Validate fields"""

        def validate_fields():
            if not entPatientID.get():
                messagebox.showerror("Error", "Please enter a patient ID")
                return False
            if not entPatientName.get():
                messagebox.showerror("Error", "Please enter a patient name")
                return False
            if not entPatientAge.get():
                messagebox.showerror("Error", "Please enter a patient age")
                return False
            if not gender_combo.get():
                messagebox.showerror("Error", "Please select a gender")
                return False
            if not entPatientDiagnosis.get():
                messagebox.showerror("Error", "Please enter a patient diagnosis")
                return False
            if not txtPatientProgressNotes.get("1.0", "end-1c"):
                messagebox.showerror("Error", "Please enter progress notes")
                return False
            if not txtPatientWard.get("1.0", "end-1c"):
                messagebox.showerror("Error", "Please enter a patient ward")
                return False
            if not txtPatientConstituency.get("1.0", "end-1c"):
                messagebox.showerror("Error", "Please enter a patient constituency")
                return False
            if not doctor_combo.get():
                messagebox.showerror("Error", "Please select a doctor")
                return False
            return True

        # Define submit function
        def submit():
            if not validate_fields():
                return
            # Get values from GUI fields
            patient_id = int(entPatientID.get())
            patient_name = entPatientName.get()
            patient_age = int(entPatientAge.get())
            gender = gender_combo.get()
            patient_diagnosis = entPatientDiagnosis.get()
            progress_notes = txtPatientProgressNotes.get()
            ward = txtPatientWard.get()
            constituency = txtPatientConstituency.get("1.0", 'end-1c')
            doctor = doctor_combo.get()
            selected_doctor_name = doctor
            mycursor.execute("SELECT doctorID FROM doctors WHERE doctorName = %s", (selected_doctor_name,))
            selected_doctor_id = mycursor.fetchone()[0]

            # Check if patient record already exists
            mycursor.execute("SELECT COUNT(*) FROM patients WHERE PatientID = %s", (patient_id,))
            count = mycursor.fetchone()[0]
            if count > 0:
                messagebox.showerror("Error", "Record already exists!\n Did you mean to update? Click 'Update' button")
                return

            # Insert record into table
            sql = "INSERT INTO patients (PatientID, PatientName, PatientAge, PatientDiagnosis, PatientGender, " \
                  "ProgressNotes, Constituency, Ward, AssignedDoctor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (patient_id, patient_name, patient_age, patient_diagnosis, gender, progress_notes, constituency, ward,
                   selected_doctor_id)
            mycursor.execute(sql, val)
            mydb.commit()
            fetch_patients()

            # Show confirmation message
            messagebox.showinfo("Success", "Record inserted successfully!")

            clear()

        def fetch_patients():
            conn = mysql.connector.connect(host="localhost", user="root", password="Legacy@96", database="pms_db")
            mycursor = conn.cursor()
            self.paliative_table.delete(*self.paliative_table.get_children())
            mycursor.execute("SELECT * FROM patients")
            rows = mycursor.fetchall()
            if len(rows) != 0:
                self.paliative_table.delete(*self.paliative_table.get_children())
                for row in rows:
                    self.paliative_table.insert('', END, values=row)
                conn.commit()
            conn.close()

        def update_count(event=None):
            # Get the selected medical condition from the combo box
            condition = combo_box.get()

            # Execute an SQL query to count the patients with the selected medical condition
            mycursor.execute("SELECT COUNT(*) FROM patients WHERE PatientDiagnosis = %s", (condition,))
            count = mycursor.fetchone()[0]

            # Update the label with the patient count
            count_label.config(text=condition + ": " + str(count))

        def patients_by_age_graph():
            mycursor.execute("SELECT PatientAge FROM patients")
            patient_data = mycursor.fetchall()

            # Extract ages from patient data
            ages = [age[0] for age in patient_data]

            # Create histogram
            fig, ax = plt.subplots(figsize=(3, 2))
            ax.hist(ages, bins=range(0, 50, 10))

            # Add labels and title
            ax.set_xlabel('Age')
            ax.set_ylabel('Number of Patients')
            ax.set_title('Patient Age Distribution')

        def show_patient_data(event):
            selected_item = self.paliative_table.selection()[0]
            patient_data = self.paliative_table.item(selected_item, "values")

            # create popup window and display patient data
            popup_window = Toplevel()
            popup_window.title("Patient Data")
            # create a frame for the labels
            PopupFrameLeft = Frame(popup_window, width=300, height=300)
            PopupFrameLeft.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            PopupFrameRight = Frame(popup_window, width=300, height=300)
            PopupFrameRight.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

            PopupFrameBottom = Frame(popup_window)
            PopupFrameBottom.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

            def delete_selected():
                """Deletes a patient record from the MySQL database."""

                # Show confirmation dialog
                confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient record?")

                # Get selected patient ID
                user_ID = patient_data[1]
                if confirm:
                    # Delete patient record from the database
                    sql = "DELETE FROM patients WHERE PatientID = %s"
                    val = (user_ID,)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    fetch_patients()

                    # Show success message
                    messagebox.showinfo("Success", "Patient record deleted successfully.")

            # create a button to edit patient data and place it in the bottom frame
            edit_button = Label(PopupFrameBottom, text="   ", width=20)
            edit_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            # delete button
            delete_button = Button(PopupFrameBottom, text="Delete patient record", bg="red", fg="white", width=20,
                                   command=delete_selected)
            delete_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

            # create labels to display patient data
            patient_id_label = Label(PopupFrameLeft, text=f"Patient ID: {patient_data[1]}")
            patient_name_label = Label(PopupFrameLeft, text=f"Patient Name: {patient_data[2]}")
            patient_age_label = Label(PopupFrameLeft, text=f"Patient Age: {patient_data[3]}")
            patient_gender_label = Label(PopupFrameLeft, text=f"Gender: {patient_data[4]}")
            patient_diagnosis_label = Label(PopupFrameLeft, text=f"Patient Diagnosis: {patient_data[5]}")
            progress_notes_label = Label(PopupFrameRight, text=f"Constituency: {patient_data[6]}")
            constituency_label = Label(PopupFrameRight, text="Progress Notes:")
            progress_notes_text = Text(PopupFrameRight, width=30, height=10, wrap="word")
            ward_label = Label(PopupFrameLeft, text=f"Ward: {patient_data[8]}")

            # arrange labels in grid
            patient_id_label.grid(row=0, column=0, padx=10, pady=5)
            patient_name_label.grid(row=1, column=0, padx=10, pady=5)
            patient_age_label.grid(row=2, column=0, padx=10, pady=5)
            patient_gender_label.grid(row=3, column=0, padx=10, pady=5)
            patient_diagnosis_label.grid(row=4, column=0, padx=10, pady=5)
            progress_notes_label.grid(row=0, column=0, padx=10, pady=5)
            constituency_label.grid(row=1, column=0, padx=1, pady=5, sticky="n")
            progress_notes_text.grid(row=1, column=1, padx=1, pady=5)
            progress_notes_text.insert(END, patient_data[7])
            progress_notes_text.config(state=DISABLED)
            ward_label.grid(row=5, column=0, padx=10, pady=5)

            popup_window.grid_rowconfigure(1, weight=1)
            popup_window.grid_columnconfigure(0, weight=1)

            popup_window.mainloop()

        def fetch_patient_data(event):
            selected_item = self.paliative_table.selection()[0]
            patient_data = self.paliative_table.item(selected_item, "values")
            print(patient_data[8])
            entPatientID.delete(0, END)
            entPatientID.insert(0, patient_data[1])
            entPatientName.delete(0, END)
            entPatientName.insert(0, patient_data[2])
            entPatientAge.delete(0, END)
            entPatientAge.insert(0, patient_data[4])
            gender_combo.delete(0, END)
            gender_combo.insert(0, patient_data[5])
            entPatientDiagnosis.delete(0, END)
            entPatientDiagnosis.insert(0, patient_data[3])
            txtPatientProgressNotes.delete(0, END)
            txtPatientProgressNotes.insert(0, patient_data[6])
            txtPatientConstituency.delete('1.0', END)
            txtPatientConstituency.insert(END, patient_data[7])
            txtPatientWard.delete(0, END)
            txtPatientWard.insert(0, patient_data[8])

            # delete patient record

        def delete_patient():
            """Deletes a patient record from the MySQL database."""

            # Show confirmation dialog
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient record?")

            # Get selected patient ID
            selected_item = entPatientID.get()
            if confirm:
                # Delete patient record from the database
                sql = "DELETE FROM patients WHERE PatientID = %s"
                val = (selected_item,)
                mycursor.execute(sql, val)
                mydb.commit()
                fetch_patients()

                # Show success message
                messagebox.showinfo("Success", "Patient record deleted successfully.")

        def get_selected_doctor_id(event):
            selected_doctor_name = doctor_combo.get()
            mycursor.execute("SELECT doctorID FROM doctors WHERE doctorName = %s", (selected_doctor_name,))
            selected_doctor_id = mycursor.fetchone()[0]
            print("Selected DoctorID:", selected_doctor_id)

        def show_graphs():
            analysis_popup = Toplevel()
            analysis_popup.title("Data Analysis")

            mycursor.execute("SELECT PatientAge FROM patients")
            patient_data = mycursor.fetchall()

            # Extract ages from patient data
            ages = [age[0] for age in patient_data]

            # Create histogram
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.hist(ages, bins=range(0, 50, 10))
            fig2 = plot_patient_data_by_diagnosis()

            # Add labels and title
            ax.set_xlabel('Age')
            ax.set_ylabel('Number of Patients')
            ax.set_title('Patient Distribution by Age')

            canvas_frame = tk.Frame(analysis_popup, width=600, height=500)
            canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

            p_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            p_canvas.draw()
            p_canvas.get_tk_widget().grid(row=1, column=1, sticky="nsew")
            canvas2 = FigureCanvasTkAgg(fig2, master=canvas_frame)
            canvas2.draw()
            canvas2.get_tk_widget().grid(row=1, column=2, sticky="nsew")

            analysis_popup.grid_rowconfigure(1, weight=1)
            analysis_popup.grid_columnconfigure(0, weight=1)

            analysis_popup.mainloop()

        def plot_patient_data_by_diagnosis():
            # Execute the query
            mycursor.execute("SELECT PatientDiagnosis, COUNT(*) as count FROM patients GROUP BY PatientDiagnosis")
            result = mycursor.fetchall()

            # Create the graph
            x = [row[0] for row in result]
            y = [row[1] for row in result]
            fig = plt.figure(figsize=(5, 5))
            plt.bar(x, y)
            plt.title("Patients by Diagnosis")
            plt.xlabel("Diagnosis")
            plt.ylabel("Count")

            # Return the graph
            return fig

        def update_selected_patient_data():
            patient_id = entPatientID.get()

            if not patient_id:
                messagebox.showerror("Error", "Please select a patient in the table below to update\n"
                                              "👆Double click to see more details about patient", parent=self.root)
                return

            # Get the updated values for the patient
            patient_id = int(entPatientID.get())
            patient_name = entPatientName.get()
            patient_age = int(entPatientAge.get())
            gender = gender_combo.get()
            patient_diagnosis = entPatientDiagnosis.get()
            progress_notes = txtPatientProgressNotes.get()
            ward = txtPatientWard.get()
            constituency = txtPatientConstituency.get("1.0", 'end-1c')
            doctor = doctor_combo.get()
            selected_doctor_name = doctor
            mycursor.execute("SELECT doctorID FROM doctors WHERE doctorName = %s", (selected_doctor_name,))
            selected_doctor_id = mycursor.fetchone()[0]

            sql = "UPDATE patients SET PatientName = %s, PatientAge = %s, PatientGender = %s, PatientDiagnosis = %s, " \
                  "ProgressNotes = %s, Constituency = %s, Ward = %s, AssignedDoctor = %s WHERE PatientID = %s"

            # Execute the query and pass the updated values
            mycursor.execute(sql, (
                patient_name, patient_age, gender, patient_diagnosis, progress_notes, constituency, ward,
                selected_doctor_id, patient_id))

            # Commit the changes to the database
            mydb.commit()
            clear()
            # Show a message indicating the update was successful
            messagebox.showinfo("Success", "Patient record updated successfully", parent=self.root)

            # Reload the patient data in the table
            fetch_patients()

        def reports():
            # create a new window
            window = tk.Toplevel()

            # set the window title
            window.title("Reports")

            # create a frame for the buttons
            button_frame = tk.Frame(window)
            button_frame.pack(side=tk.TOP, fill=tk.X)

            # create the buttons
            def fetch_all_patients():
                mycursor.execute("SELECT * FROM patients")
                return mycursor.fetchall()

            def generate_pdf():
                # Create a PDF object
                pdf = FPDF()

                # Add a page to the PDF
                pdf.add_page()

                # Set the font and font size
                pdf.set_font("Arial", size=12)
                mycursor.execute("SELECT ProgressNotes, PatientName FROM patients ORDER BY ProgressNotes")
                results = mycursor.fetchall()

                # Add the data to the PDF
                for constituency, patient in results:
                    pdf.cell(50, 10, constituency, border=1)
                    pdf.cell(50, 10, patient, border=1)
                    pdf.ln()

                # Save the PDF
                pdf_file = "All patients report.pdf"
                pdf.output(pdf_file)

                # Pop an alert to show whether the process succeeded
                messagebox.showinfo("Success", "Report generated and saved to PDF")

                # Open the file as soon as it is saved
                os.startfile(pdf_file)

            # Define a function to handle the button click event

            def table():
                # Create a connection to the MySQL database

                # Create the root window
                root = tk.Tk()

                # Create the outer table
                outer_table = tk.Frame(root)
                outer_table.pack()

                # Create the inner table for the patient data
                inner_table = tk.Frame(outer_table)
                inner_table.pack()

                # Create the header cells for the inner table
                constituency_header = tk.Label(inner_table, text="Constituency", font=("Arial", 14), borderwidth=1,
                                               relief=tk.RAISED)
                constituency_header.grid(row=0, column=0)
                patient_header = tk.Label(inner_table, text="Patient Name", font=("Arial", 14), borderwidth=1,
                                          relief=tk.RAISED)
                patient_header.grid(row=0, column=1)

                # Fetch the patient data from the database grouped by constituency
                mycursor.execute("SELECT ProgressNotes, PatientName FROM patients ORDER BY ProgressNotes")
                results = mycursor.fetchall()

                # Create variables to hold the current constituency and row index
                current_constituency = None
                current_row = 0

                # Create cells for each patient in each constituency
                for result in results:
                    constituency = result[0]
                    patient = result[1]

                    # If the constituency has changed, create a new row in the table
                    if constituency != current_constituency:
                        constituency_label = tk.Label(inner_table, text=constituency, bd=1)
                        constituency_label.grid(row=current_row + 1, column=0)
                        current_constituency = constituency
                        current_row += 1

                    # Create a cell for the patient in the same row as the constituency
                    patient_label = tk.Label(inner_table, text=patient, bd=1)
                    patient_label.grid(row=current_row, column=1)

                    # Move to the next row
                    current_row += 1

                    # Add gridlines to the table
                    for i in range(2):
                        inner_table.grid_columnconfigure(i, weight=1, minsize=100)
                    for i in range(current_row + 1):
                        inner_table.grid_rowconfigure(i, weight=1, minsize=30)

                pdf_button = tk.Button(outer_table, text="Print Report", command=generate_pdf, font=("Arial", 14),
                                       bg="darkgreen", fg="white")
                pdf_button.pack(padx=10, pady=30, side=tk.BOTTOM)

                # Start the event loop

            patient_summary_button = tk.Button(button_frame, text="Patient Summary Report")
            patient_summary_button.pack(side=tk.LEFT)

            demographic_report_button = tk.Button(button_frame, text="Demographic Report",
                                                  command=table)
            demographic_report_button.pack(side=tk.LEFT)

            disease_prevalence_button = tk.Button(button_frame, text="Disease Prevalence Report",
                                                  command=generate_disease_prevalence_report)
            disease_prevalence_button.pack(side=tk.LEFT)

            # create a label for the content area
            content_frame = tk.Frame(window)
            content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # create a table for the patient data
            columns = ("ID", "PatientID", "PatientName", "PatientAge", "PatientGender",
                       "PatientDiagnosis", "ProgressNotes", "Constituency", "Ward")
            table = ttk.Treeview(content_frame, columns=columns, show='headings')
            table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            rowz = fetch_all_patients()
            # insert the data into the table
            for row in rowz:
                table.insert("", "end", values=row)

            # create a function to generate the printable report
            def print_report():
                # Fetch all patients
                patients = fetch_all_patients()

                # Generate PDF filename
                filename = "patients_report.pdf"
                if os.path.exists(filename):
                    os.remove(filename)

                # Create a new PDF file
                c = canvas.Canvas(filename, pagesize=letter)

                # Define table columns and widths
                table_cols = ["ID", "PatientID", "PatientName", "PatientAge", "PatientGender", "PatientDiagnosis",
                              "ProgressNotes", "Constituency", "Ward"]
                col_widths = [50, 70, 120, 50, 50, 150, 150, 80, 80]

                # Draw table header
                x = 40
                y = 750
                for i in range(len(table_cols)):
                    c.drawString(x, y, table_cols[i])
                    x += col_widths[i]

                # Draw table rows
                y -= 20
                for patient in patients:
                    x = 40
                    for i in range(len(table_cols)):
                        c.drawString(x, y, str(patient[i]))
                        x += col_widths[i]
                    y -= 20

                # Save and close the PDF file
                c.save()
                # Show message box on successful save
                messagebox.showinfo("Save Successful", f"Patients report saved to {filename}")

                # Open the PDF file
                os.system(f"open {filename}")

            # create a button to print the report
            print_button = tk.Button(content_frame, text="Print Patients Report", bg="darkgreen", font=("Arial", 12),
                                     fg="white", command=print_report)
            print_button.pack(side=tk.BOTTOM, padx=10, pady=30, )

        def search_data():
            selected_column = search_combo.get()
            search_value = txtsearch.get()

            # clear the table
            self.paliative_table.delete(*self.paliative_table.get_children())

            # execute query to retrieve data based on selected column and search value
            if selected_column == "Patient ID":
                query = "SELECT * FROM patients WHERE PatientID LIKE %s"
                search_value = f"%{search_value}%"
            elif selected_column == "Patient Name":
                query = "SELECT * FROM patients WHERE PatientName LIKE %s"
                search_value = f"%{search_value}%"
            else:
                query = "SELECT * FROM patients WHERE PatientDiagnosis LIKE %s"
                search_value = f"%{search_value}%"

            mycursor.execute(query, (search_value,))

            results = mycursor.fetchall()

            # insert data into the table
            for result in results:
                self.paliative_table.insert("", "end", values=result)

        def exit_window():
            root.destroy()

        def generate_disease_prevalence_report():
            # SQL query to fetch patient data
            sql_query = "SELECT ProgressNotes, PatientDiagnosis, COUNT(*) FROM patients GROUP BY ProgressNotes, PatientDiagnosis"

            # Execute SQL query
            mycursor.execute(sql_query)
            result_set = mycursor.fetchall()

            # Create a pretty table and add columns
            table = PrettyTable()
            table.field_names = ["Constituency", "Disease", "Count"]

            # Add rows to the table
            for row in result_set:
                constituency, disease, count = row
                table.add_row([constituency, disease, count])

            # Close the database connection
            mycursor.close()
            mydb.close()

            # Create a new window to display the table
            table_window = tk.Toplevel()
            table_window.title("Disease Prevalence Report")

            # Create a label and set its text to the table
            table_label = tk.Label(table_window, text=str(table))
            table_label.pack()

            # Create a "print report" button that saves the table as a PDF
            def print_report():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Add the table to the PDF
                for item in str(table).split("\n"):
                    pdf.cell(200, 10, txt=item, ln=1)

                # Save the PDF
                pdf_file = "disease_prevalence_report.pdf"
                pdf.output(pdf_file)
                print("Report saved as " + pdf_file)

                try:
                    messagebox.showinfo("Print Report", "The report has been saved as a PDF.")
                    os.startfile(pdf_file)

                except:
                    messagebox.showerror("Print Report", "An error occurred while saving the report.")

            report_button = tk.Button(table_window, text="Print Report", command=print_report, bg="darkgreen",
                                      font=("Arial", 12), fg="white")
            report_button.pack(padx=10, pady=30, side=tk.BOTTOM, )

        def add_doctor():
            # Create a new window
            add_doctor_window = tk.Toplevel()
            add_doctor_window.title("Add Doctor")

            # Create a frame to hold the content
            content_frame = tk.Frame(add_doctor_window, padx=10, pady=10)
            content_frame.pack()

            doctor_id_label = tk.Label(content_frame, text="Doctor ID", font=("Arial", 12))
            doctor_id_label.grid(row=0, column=0, padx=10, pady=10)

            doctor_id_entry = tk.Entry(content_frame, font=("Arial", 12))
            doctor_id_entry.grid(row=0, column=1, padx=10, pady=10)

            # Create a label and entry for the doctor's name
            name_label = tk.Label(content_frame, text="Doctor's Name", font=("Arial", 12))
            name_label.grid(row=1, column=0, padx=10, pady=10)

            name_entry = tk.Entry(content_frame, font=("Arial", 12))
            name_entry.grid(row=1, column=1, padx=10, pady=10)

            # Create a label and entry for the doctor's phone number
            phone_label = tk.Label(content_frame, text="Phone Number", font=("Arial", 12))
            phone_label.grid(row=2, column=0, padx=10, pady=10)

            phone_entry = tk.Entry(content_frame, font=("Arial", 12))
            phone_entry.grid(row=2, column=1, padx=10, pady=10)

            # Create a label and entry for the doctor's email address
            email_label = tk.Label(content_frame, text="Email Address", font=("Arial", 12))
            email_label.grid(row=3, column=0, padx=10, pady=10)

            email_entry = tk.Entry(content_frame, font=("Arial", 12))
            email_entry.grid(row=3, column=1, padx=10, pady=10)

            # Create a label and entry for the doctor's password
            shift_label = tk.Label(content_frame, text="Doctor shift", font=("Arial", 12))
            shift_label.grid(row=4, column=0, padx=10, pady=10)

            shift_entry = tk.Entry(content_frame, font=("Arial", 12))
            shift_entry.grid(row=4, column=1, padx=10, pady=10)

            # Create a label and entry for the doctor's specialization
            specialization_label = tk.Label(content_frame, text="Specialization", font=("Arial", 12))
            specialization_label.grid(row=5, column=0, padx=10, pady=10)

            specialization_entry = tk.Entry(content_frame, font=("Arial", 12))
            specialization_entry.grid(row=5, column=1, padx=10, pady=10)

            # add data to the database
            def add_doctor_to_database():
                # Get the values from the entries
                doctor_id = doctor_id_entry.get()
                name = name_entry.get()
                phone = phone_entry.get()
                email = email_entry.get()
                shift = shift_entry.get()
                specialization = specialization_entry.get()

                # Insert the data into the database
                sql_query = "INSERT INTO doctors (doctorID, doctorName, doctorSpecialty, doctorShift, phoneNumber, emailAddress) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (doctor_id, name, specialization, shift, phone, email)
                mycursor.execute(sql_query, values)
                mydb.commit()

                # Close the database connection
                mycursor.close()
                mydb.close()

                # Close the window
                add_doctor_window.destroy()

                # Display a message box to confirm that the data was added
                messagebox.showinfo("Add Doctor", "The doctor was added successfully.")

            # Create a button to add the doctor to the database
            add_doctor_button = tk.Button(content_frame, text="Add Doctor", command=add_doctor_to_database,
                                          bg="darkgreen",
                                          font=("Arial", 12), fg="white")
            add_doctor_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        lbltitle = Label(self.root, text="PALLIATIVE CARE MANAGEMENT SYSTEM", bd=15,
                         font=("times new roman", 30, "bold"), fg="darkgreen", relief=RIDGE, bg="white", padx=2, pady=4)

        lbltitle.pack(side=TOP, fill=X)

        img = Image.open(path1)
        img = img.resize((50, 50), Image.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        b1 = Button(self.root, image=self.photoimg, borderwidth=0)
        b1.place(x=70, y=15)

        # ==================DATA FRAME========================
        DataFrame = Frame(self.root, bd=10, relief=RIDGE, bg="white", padx=5)
        DataFrame.place(x=0, y=75, relwidth=1.0, height=650)

        DataFrameLeft = LabelFrame(DataFrame, bd=10, relief=RIDGE, bg="white", padx=5, text="Add Patient",
                                   fg="darkgreen", font=("arial", 12, "bold"))
        DataFrameLeft.grid(row=0, column=0, sticky="nsew")

        DataFrameRight = LabelFrame(DataFrame, bd=10, relief=RIDGE, bg="white", padx=5, text="Dashboard",
                                    fg="darkgreen", font=("arial", 12, "bold"))
        DataFrameRight.grid(row=0, column=1, sticky="nsew")
        # set the column and row weights to make the frames expand to fill the available space
        DataFrame.columnconfigure(0, weight=0)
        DataFrame.columnconfigure(1, weight=9)

        btnAnalysis = Button(DataFrameRight, text="Analysis", font=("arial", 12, "bold"), bg="darkgreen", fg="white",
                             command=show_graphs)
        btnAnalysis.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        btnReport = Button(DataFrameRight, text="Generate Reports", font=("arial", 12, "bold"), bg="darkgreen",
                           fg="white", command=reports)
        btnReport.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Data Frame right to hold the combo box and count_label
        ComboFrame = LabelFrame(DataFrameRight, bd=2, relief=RIDGE, bg="white", padx=5,
                                fg="darkgreen", font=("arial", 12, "bold"))
        ComboFrame.grid(row=1, column=0, sticky="nsew")

        """"Images section"""
        img1 = Image.open("C:/Users/Gideon Kiprotich/Downloads/meds.jpg")
        img1 = img1.resize((150, 135), Image.LANCZOS)
        self.photoimg1 = ImageTk.PhotoImage(img1)
        b1 = Button(DataFrameRight, image=self.photoimg1, borderwidth=0, )
        b1.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        img2 = Image.open(path2)
        img2 = img2.resize((150, 80), Image.LANCZOS)
        self.photoimg2 = ImageTk.PhotoImage(img2)
        b1 = Button(DataFrameRight, image=self.photoimg2, borderwidth=0)
        b1.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        img3 = Image.open(path3)
        img3 = img3.resize((150, 80), Image.LANCZOS)
        self.photoimg3 = ImageTk.PhotoImage(img3)
        b1 = Button(DataFrameRight, image=self.photoimg3, borderwidth=0)
        b1.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

        # Create a combo box for selecting the medical condition
        conditions = ["cancer", "diabetes", "heart disease", "asthma"]
        combo_box = tk.ttk.Combobox(ComboFrame, values=conditions)

        # Bind the ComboboxSelected event to the update_count function
        combo_box.bind("<<ComboboxSelected>>", update_count)
        filter_title = tk.Label(ComboFrame, text="Filter by diagnosis", font=("arial", 14, "bold"))

        # Create a label to display the patient count
        count_label = tk.Label(ComboFrame, text="Patient count: ", font=("arial", 12, "bold"))

        # Pack the combo box, button, and label into the window
        filter_title.grid(row=0, column=0, padx=5, pady=5)
        combo_box.grid(row=1, column=0, padx=5, pady=5)
        count_label.grid(row=2, column=0, padx=5, pady=5)

        # ==================BUTTONS LAYOUT========================

        ButtonFrame = Frame(self.root, bd=10, relief=RIDGE, bg="white", padx=5)
        ButtonFrame.place(x=0, y=400, relwidth=1.0, height=65)

        # ==================MAIN BUTTONS========================
        btnAddData = Button(ButtonFrame, text="Add New Doctor", font=("arial", 12, "bold"), bg="darkgreen", fg="white",
                            command=add_doctor)
        btnAddData.grid(row=0, column=0, padx=2, pady=2)

        btnUpdate = Button(ButtonFrame, text="Update Patient", font=("arial", 12, "bold"), bg="darkgreen", fg="white",
                           command=update_selected_patient_data)
        btnUpdate.grid(row=0, column=1, padx=2, pady=2)

        btnDelete = Button(ButtonFrame, text="Delete Patient", font=("arial", 12, "bold"), bg="red", fg="white",
                           command=delete_patient)
        btnDelete.grid(row=0, column=2, padx=2, pady=2)

        btnReset = Button(ButtonFrame, text="Reset Fields", font=("arial", 12, "bold"), bg="darkgreen", fg="white",
                          command=clear)
        btnReset.grid(row=0, column=3, padx=2, pady=2)

        btnExit = Button(ButtonFrame, text="Exit App", font=("arial", 12, "bold"), bg="darkgreen", fg="white",
                         command=exit_window)
        btnExit.grid(row=0, column=4, padx=2, pady=2)

        lblSearchBy = Label(ButtonFrame, text="Search By", font=("arial", 12, "bold"), bg="red", fg="white", width=10,
                            )
        lblSearchBy.grid(row=0, column=5, padx=2, pady=2, sticky=W)

        search_combo = ttk.Combobox(ButtonFrame, font=("arial", 12, "bold"), width=13, state="readonly")
        search_combo["values"] = ("Patient ID", "Patient Name", "Diagnosis")
        search_combo.grid(row=0, column=6, padx=5, pady=2)
        search_combo.current(0)

        txtsearch = Entry(ButtonFrame, font=("arial", 12, "bold"), bd=3, relief=RIDGE, width=13)
        txtsearch.grid(row=0, column=7, padx=5, pady=2)

        searchBtn = Button(ButtonFrame, text="Search", font=("arial", 12, "bold"), bg="darkgreen", fg="white", width=10,
                           command=search_data)
        searchBtn.grid(row=0, column=8, padx=2, pady=2)

        showAll = Button(ButtonFrame, text="Show All", font=("arial", 12, "bold"), bg="darkgreen", fg="white", width=13,
                         command=fetch_patients)
        showAll.grid(row=0, column=9, padx=2, pady=2)

        # ==================LABEL AND ENTRY========================
        lblPatientID = Label(DataFrameLeft, text="Reference number:", font=("Arial", 14), padx=2, width=15, anchor="w",
                             justify=LEFT)
        lblPatientID.grid(row=0, column=0, sticky=W)

        entPatientID = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        entPatientID.grid(row=0, column=1, padx=2, pady=5, sticky=W)

        # align label text to the left

        lblPatientName = Label(DataFrameLeft, text="Patient Name:", font=("Arial", 14), width=15, anchor="w",
                               justify=LEFT)
        lblPatientName.grid(row=1, column=0, padx=2, pady=5, sticky=W)

        entPatientName = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        entPatientName.grid(row=1, column=1, padx=2, pady=5, sticky=W)

        lblPatientAge = Label(DataFrameLeft, text="Patient Age:", font=("Arial", 14), width=15, anchor="w",
                              justify=LEFT)
        lblPatientAge.grid(row=2, column=0, padx=2, pady=5, sticky=W)

        entPatientAge = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        entPatientAge.grid(row=2, column=1, padx=2, pady=5, sticky=W)

        lblRefno = Label(DataFrameLeft, text="Gender:", font=("Arial", 14), padx=2, width=15, anchor="w",
                         justify=LEFT)
        lblRefno.grid(row=3, column=0, sticky=W)

        gender_combo = ttk.Combobox(DataFrameLeft, font=("arial", 14, "bold"), state="readonly", width=15)
        gender_combo["values"] = ("Male", "Female", "Other")
        gender_combo.grid(row=3, column=1, padx=2, pady=5, sticky=W)

        lblPatientDiagnosis = Label(DataFrameLeft, text="Patient Diagnosis:", font=("Arial", 14), anchor="w",
                                    justify=LEFT)
        lblPatientDiagnosis.grid(row=4, column=0, padx=2, pady=5, sticky=W)

        entPatientDiagnosis = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        entPatientDiagnosis.grid(row=4, column=1, padx=2, pady=5, sticky=W)

        lblPatientConstituency = Label(DataFrameLeft, text="Progress Notes:", font=("Arial", 14), anchor="e",
                                       justify=RIGHT)
        lblPatientConstituency.grid(row=5, column=0, padx=5, pady=5, sticky=W)

        txtPatientConstituency = Text(DataFrameLeft, font=("Arial", 14), bd=3, width=16, height=3, )
        txtPatientConstituency.grid(row=5, column=1, padx=5, pady=5, sticky=W)

        lblPatientProgressNotes = Label(DataFrameLeft, text="Constituency:", font=("Arial", 14), anchor="e",
                                        justify=RIGHT)
        lblPatientProgressNotes.grid(row=0, column=3, padx=5, pady=5, sticky=W)

        txtPatientProgressNotes = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        txtPatientProgressNotes.grid(row=0, column=4, padx=5, pady=5, sticky=W)

        lblPatientWard = Label(DataFrameLeft, text="Ward:", font=("Arial", 14), anchor="e",
                               justify=RIGHT)
        lblPatientWard.grid(row=1, column=3, padx=5, pady=5, sticky=W)

        txtPatientWard = Entry(DataFrameLeft, font=("Arial", 14), bd=3, width=16)
        txtPatientWard.grid(row=1, column=4, padx=5, pady=5, sticky=W)

        lblDoctorID = Label(DataFrameLeft, text="Assigned Doctor:", font=("Arial", 14), anchor="e",
                            justify=RIGHT)
        lblDoctorID.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        mycursor.execute("SELECT doctorName FROM doctors")
        rows = mycursor.fetchall()

        doctor_names = [row[0] for row in rows]

        doctor_combo = ttk.Combobox(DataFrameLeft, font=("arial", 12), state="readonly", width=15)
        doctor_combo["values"] = doctor_names
        doctor_combo.grid(row=2, column=4, padx=5, pady=5, sticky=W)
        doctor_combo.current(0)

        doctor_combo.bind("<<ComboboxSelected>>", get_selected_doctor_id)

        btnSubmit = Button(DataFrameLeft, text="Submit", font=("Arial", 14), bg="darkgreen", fg="white", width=18,
                           command=submit)
        btnSubmit.grid(row=5, column=4, padx=5, pady=5, sticky=E)

        # ==================TABLE FRAME CONTAINER========================
        FrameDetails = Frame(self.root, bd=10, relief=RIDGE)
        FrameDetails.place(x=0, y=460, relwidth=1.0, height=180)

        # ==================TABLE FRAME========================
        TableFrame = Frame(FrameDetails, bd=1, relief=RIDGE)
        TableFrame.place(x=0, y=1, relwidth=1.0, height=180)

        scroll_x = Scrollbar(TableFrame, orient=HORIZONTAL)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y = Scrollbar(TableFrame, orient=VERTICAL)
        scroll_y.pack(side=RIGHT, fill=Y)

        # ==================TABLE========================

        self.paliative_table = ttk.Treeview(TableFrame,
                                            columns=("ID", "PatientID", "PatientName", "PatientAge", "PatientGender",
                                                     "PatientDiagnosis", "ProgressNotes", "Constituency",
                                                     "Ward"), xscrollcommand=scroll_x.set,
                                            yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)

        scroll_x.config(command=self.paliative_table.xview)
        scroll_y.config(command=self.paliative_table.yview)

        # Add gridlines to table headings
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Calibri", 12, "bold"), borderwidth=1, relief='solid')
        style.configure("Treeview", highlightthickness=1, borderwidth=1, font=("Calibri", 11))
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        style.map("Treeview", foreground=[('selected', 'black')], background=[('selected', '#EAECEE')])

        self.paliative_table["show"] = "headings"

        self.paliative_table.heading("ID", text="SNo.")
        self.paliative_table.heading("PatientID", text="Patient ID")
        self.paliative_table.heading("PatientName", text="Patient Name")
        self.paliative_table.heading("PatientAge", text="Patient Age")
        self.paliative_table.heading("PatientGender", text="Gender")
        self.paliative_table.heading("PatientDiagnosis", text="Patient Diagnosis")
        self.paliative_table.heading("ProgressNotes", text="Progress Notes")
        self.paliative_table.heading("Constituency", text="Constituency")
        self.paliative_table.heading("Ward", text="Ward")

        self.paliative_table.pack(fill=BOTH, expand=1)

        self.paliative_table.column("ID", width=10, anchor="center")
        self.paliative_table.column("PatientID", width=100, anchor="center")
        self.paliative_table.column("PatientName", width=100, anchor="center")
        self.paliative_table.column("PatientAge", width=100, anchor="center")
        self.paliative_table.column("PatientGender", width=100, anchor="center")
        self.paliative_table.column("PatientDiagnosis", width=100, anchor="center")
        self.paliative_table.column("ProgressNotes", width=100, anchor="center")
        self.paliative_table.column("Constituency", width=100, anchor="center")
        self.paliative_table.column("Ward", width=100, anchor="center")

        fetch_patients()
        patients_by_age_graph()
        self.paliative_table.bind("<Double-1>", show_patient_data)

        self.paliative_table.bind("<ButtonRelease-1>", fetch_patient_data)


if __name__ == "__main__":
    root = Tk()
    app = PalliativeCare(root)
    root.mainloop()
