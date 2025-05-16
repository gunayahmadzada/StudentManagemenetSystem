from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
import time
import pandas
import ttkthemes
import pymysql
import re
import qrcode
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import datetime
import os

current_user = None
current_role = None
attendance_log_path = 'attendance_log.txt'
most_recent_access = {}
time_between_logs_th = 5


def toplevel_data(title, button_text, command):
    global idEntry, nameEntry, surnameEntry, phoneEntry, genderEntry, birthEntry, mailEntry, programEntry, top_window
    top_window = Toplevel()
    top_window.title(title)
    top_window.grab_set()
    top_window.resizable(False, False)
    idLabel = Label(top_window, text="ID", font=("Arial", 20, 'bold'))
    idLabel.grid(row=0, column=0, padx=20, pady=10, sticky=W)
    idEntry = Entry(top_window, font=("Arial", 15), width=20, validate='key', validatecommand=(top_window.register(lambda text: text.isdigit() or text == ''), '%P'))
    idEntry.grid(row=0, column=1, padx=20, pady=10)

    nameLabel = Label(top_window, text="Name", font=("Arial", 20, 'bold'))
    nameLabel.grid(row=1, column=0, padx=20, pady=10, sticky=W)
    nameEntry = Entry(top_window, font=("Arial", 15), width=20, validate='key', validatecommand=(top_window.register(lambda text: text.isalpha() or text == ''), '%P'))
    nameEntry.grid(row=1, column=1, padx=20, pady=10)

    surnameLabel = Label(top_window, text="Surname", font=("Arial", 20, 'bold'))
    surnameLabel.grid(row=2, column=0, padx=20, pady=10, sticky=W)
    surnameEntry = Entry(top_window, font=("Arial", 15), width=20, validate='key', validatecommand=(top_window.register(lambda text: text.isalpha() or text == ''), '%P'))
    surnameEntry.grid(row=2, column=1, padx=20, pady=10)

    phoneLabel = Label(top_window, text="Mobile Number", font=("Arial", 20, 'bold'))
    phoneLabel.grid(row=3, column=0, padx=20, pady=10, sticky=W)
    phoneEntry = Entry(top_window, font=("Arial", 15), width=20, validate='key', validatecommand=(top_window.register(lambda text: (text.isdigit() or text == '') and len(text) <= 10), '%P'))
    phoneEntry.grid(row=3, column=1, padx=20, pady=10)

    genderLabel = Label(top_window, text="Gender", font=("Arial", 20, 'bold'))
    genderLabel.grid(row=4, column=0, padx=20, pady=10, sticky=W)
    genderEntry = ttk.Combobox(top_window, font=("Arial", 15), width=20, state='readonly')
    genderEntry['values'] = ("Male", "Female")
    genderEntry.grid(row=4, column=1, padx=20, pady=10)

    birthLabel = Label(top_window, text="Date of Birth", font=("Arial", 20, 'bold'))
    birthLabel.grid(row=5, column=0, padx=20, pady=10, sticky=W)
    birthEntry = Calendar(top_window, selectmode='day', year=2000, month=1, day=1, font=("Arial", 15), width=20)
    birthEntry.grid(row=5, column=1, padx=20, pady=10)

    mailLabel = Label(top_window, text="Email", font=("Arial", 20, 'bold'))
    mailLabel.grid(row=6, column=0, padx=20, pady=10, sticky=W)
    mailEntry = Entry(top_window, font=("Arial", 15), width=20)
    mailEntry.grid(row=6, column=1, padx=20, pady=10)

    programLabel = Label(top_window, text="Program of Study", font=("Arial", 20, 'bold'))
    programLabel.grid(row=7, column=0, padx=20, pady=10, sticky=W)
    programEntry = Entry(top_window, font=("Arial", 15), width=20)
    programEntry.grid(row=7, column=1, padx=20, pady=10)

    student_button = ttk.Button(top_window, text=button_text, command=command)
    student_button.grid(row=8, columnspan=2, pady=20)

    if title == 'Update Student':
        indexing = studentTable.focus()
        content = studentTable.item(indexing)
        list_data = content['values']
        idEntry.insert(0, list_data[0])
        nameEntry.insert(0, list_data[1])
        surnameEntry.insert(0, list_data[2])
        phoneEntry.insert(0, list_data[3])
        genderEntry.insert(0, list_data[4])
        birthEntry.selection_set(list_data[5])
        mailEntry.insert(0, list_data[6])
        programEntry.insert(0, list_data[7])


def generate_qr_code(student_id, name=None, surname=None):
    if not os.path.exists('qr_codes'):
        os.makedirs('qr_codes')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{student_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_path = f'qr_codes/{student_id}.{name}_{surname}.png'
    img.save(qr_path)
    return qr_path


def add_data():
    if idEntry.get() == '' or nameEntry.get() == '' or surnameEntry.get() == '' or phoneEntry.get() == '' or genderEntry.get() == '' or birthEntry.get_date() == '' or mailEntry.get() == '' or programEntry.get() == '':
        messagebox.showerror('Error', 'Please fill all fields', parent=top_window)
    elif not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', mailEntry.get()):
        messagebox.showerror('Error', 'Invalid email address. Please enter a valid email.', parent=top_window)
    else:
        try:
            query = 'INSERT INTO students VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor.execute(query, (idEntry.get(), nameEntry.get(), surnameEntry.get(), phoneEntry.get(), genderEntry.get(), birthEntry.get_date(), mailEntry.get(), programEntry.get(), current_date, current_time))
            con.commit()

            student_id = idEntry.get()
            generate_qr_code(student_id, nameEntry.get(), surnameEntry.get())

            result = messagebox.askyesno('Confirm', 'Data added successfully. Do you want to add another student?', parent=top_window)
            if result:
                idEntry.delete(0, END)
                nameEntry.delete(0, END)
                surnameEntry.delete(0, END)
                phoneEntry.delete(0, END)
                genderEntry.delete(0, END)
                birthEntry.selection_clear()
                mailEntry.delete(0, END)
                programEntry.delete(0, END)
            else:
                top_window.destroy()
        except:
            messagebox.showerror('Error', 'ID is available. It should be unique.', parent=top_window)
            return

        query = 'SELECT * FROM students'
        cursor.execute(query)
        db_data = cursor.fetchall()
        studentTable.delete(*studentTable.get_children())
        for data in db_data:
            studentTable.insert('', END, values=data)


def search_data():
    query = 'SELECT * FROM students WHERE id=%s or name=%s or surname=%s or mobile_number=%s or gender=%s or date_of_birth=%s or email=%s or study_program=%s'
    cursor.execute(query, (idEntry.get(), nameEntry.get(), surnameEntry.get(), phoneEntry.get(), genderEntry.get(), birthEntry.get_date(), mailEntry.get(), programEntry.get()))
    studentTable.delete(*studentTable.get_children())
    db_data = cursor.fetchall()
    for data in db_data:
        studentTable.insert('', END, values=data)
    top_window.destroy()


def delete_student():
    indexing = studentTable.focus()
    if not indexing:
        messagebox.showerror('Error', 'Please select a user to delete', parent=window)
        return

    content = studentTable.item(indexing)
    content_id = content['values'][0]

    if messagebox.askyesno('Confirm', 'Are you sure you want to delete this user?', parent=window):
        query = 'DELETE FROM students WHERE id=%s'
        cursor.execute(query, content_id)
        con.commit()
        show_student()
        messagebox.showinfo("Confirm", f"The student is deleted successfully")


def update_data():
    query = 'UPDATE students SET name=%s, surname=%s, mobile_number=%s, gender=%s, date_of_birth=%s, email=%s, study_program=%s, added_date=%s, added_time=%s WHERE id=%s'
    cursor.execute(query, (nameEntry.get(), surnameEntry.get(), phoneEntry.get(), genderEntry.get(), birthEntry.get_date(), mailEntry.get(), programEntry.get(), current_date, current_time, idEntry.get()))
    con.commit()
    messagebox.showinfo("Confirm", f"The student is updated successfully", parent=top_window)
    top_window.destroy()
    show_student()


def show_student():
    query = 'SELECT * FROM students'
    cursor.execute(query)
    db_data = cursor.fetchall()
    studentTable.delete(*studentTable.get_children())
    for data in db_data:
        studentTable.insert('', END, values=data)


def export_data():
    url = filedialog.asksaveasfilename(defaultextension='.csv')
    indexing = studentTable.get_children()
    newlist = []
    for index in indexing:
        content = studentTable.item(index)
        datalist = content['values']
        newlist.append(datalist)

    table = pandas.DataFrame(newlist, columns=['ID', 'Name', 'Surname', 'Mobile Number', 'Gender', 'Date of Birth', 'Email', 'Program', 'Added Date', 'Added Time'])
    table.to_csv(url, index=False)
    messagebox.showinfo("Confirm", f"The student data is saved successfully")


def exit():
    answer = messagebox.askyesno('Confirm', 'Do you want to exit?')
    if answer:
        window.destroy()
    else:
        pass


def date():
    global current_date, current_time
    current_date = time.strftime("%d-%m-%Y")
    current_time = time.strftime("%H:%M:%S")
    dateLabel.config(text=f'    Date: {current_date}\nTime: {current_time}')
    dateLabel.after(1000, date)


def connect_db():
    def connect():
        global cursor, con
        try:
            # con = pymysql.connect(host='localhost', user='root', password='20102001')
            con=pymysql.connect(host=hostEntry.get(), user=userEntry.get(), password=passwordEntry.get())
            cursor = con.cursor()
        except:
            messagebox.showerror("Error", "Invalid Details", parent=dbWindow)
            return
        try:
            query = 'CREATE DATABASE student_management_system'
            cursor.execute(query)
            query = 'USE student_management_system'
            cursor.execute(query)

            query = ('CREATE TABLE students(id INT NOT NULL PRIMARY KEY, name VARCHAR(50), surname VARCHAR(100), mobile_number VARCHAR(50), gender VARCHAR(20), date_of_birth DATE, email VARCHAR(100), study_program VARCHAR(100), added_date VARCHAR(20), added_time VARCHAR(20))')
            cursor.execute(query)

            query = ('CREATE TABLE users(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(100), role ENUM("admin", "teacher") NOT NULL)')
            cursor.execute(query)

            try:
                query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
                cursor.execute(query, ('admin', 'admin123', 'admin'))
                con.commit()
            except:
                pass
        except:
            query = 'USE student_management_system'
            cursor.execute(query)
        messagebox.showinfo("Success", "Database Connection Established", parent=dbWindow)
        dbWindow.destroy()
        show_login_window()

    dbWindow = Toplevel()
    dbWindow.grab_set()
    dbWindow.geometry("430x280+500+300")
    dbWindow.title("Database Connection")
    dbWindow.resizable(False, False)

    hostLabel = Label(dbWindow, text="Enter Host Name:", font=("Arial", 20, 'bold'))
    hostLabel.grid(row=0, column=0, padx=20)
    hostEntry = Entry(dbWindow, font=("Arial", 15), bd=2)
    hostEntry.grid(row=0, column=1, pady=20)

    userLabel = Label(dbWindow, text="Enter User Name:", font=("Arial", 20, 'bold'))
    userLabel.grid(row=1, column=0, padx=20)
    userEntry = Entry(dbWindow, font=("Arial", 15), bd=2)
    userEntry.grid(row=1, column=1, pady=20)

    passwordLabel = Label(dbWindow, text="Enter Password:", font=("Arial", 20, 'bold'))
    passwordLabel.grid(row=2, column=0, padx=20)
    passwordEntry = Entry(dbWindow, font=("Arial", 15), bd=2, show="*")
    passwordEntry.grid(row=2, column=1, pady=20)

    connectButton = ttk.Button(dbWindow, text="Connect", command=connect)
    connectButton.grid(row=3, columnspan=2, pady=20)


def show_login_window():
    def login():
        global current_user, current_role, cursor
        username = usernameEntry.get()
        password = passwordEntry.get()

        if username == '' or password == '':
            messagebox.showerror('Error', 'All fields are required', parent=loginWindow)
            return

        query = 'SELECT * FROM users WHERE username=%s AND password=%s'
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            current_user = user[1]
            current_role = user[3]
            loginWindow.destroy()
            enable_buttons_based_on_role()
        else:
            messagebox.showerror('Error', 'Invalid username or password', parent=loginWindow)

    loginWindow = Toplevel()
    loginWindow.grab_set()
    loginWindow.geometry("430x280+550+300")
    loginWindow.title("Login")
    loginWindow.resizable(False, False)

    usernameLabel = Label(loginWindow, text="Username:", font=("Arial", 20, 'bold'))
    usernameLabel.grid(row=0, column=0, padx=20, pady=20)
    usernameEntry = Entry(loginWindow, font=("Arial", 15), bd=2)
    usernameEntry.grid(row=0, column=1, padx=20, pady=20)

    passwordLabel = Label(loginWindow, text="Password:", font=("Arial", 20, 'bold'))
    passwordLabel.grid(row=1, column=0, padx=20, pady=20)
    passwordEntry = Entry(loginWindow, font=("Arial", 15), bd=2, show='*')
    passwordEntry.grid(row=1, column=1, padx=20, pady=20)

    loginButton = ttk.Button(loginWindow, text="Login", command=login)
    loginButton.grid(row=2, columnspan=2, pady=20)


def manage_users():
    if current_role != 'admin':
        messagebox.showerror('Error', 'Only administrators can manage users')
        return

    def add_user():
        if usernameEntry.get() == '' or passwordEntry.get() == '' or roleEntry.get() == '':
            messagebox.showerror('Error', 'All fields are required', parent=userWindow)
            return

        try:
            query = 'SELECT MIN(t1.id + 1) as next_id FROM users t1 LEFT JOIN users t2 ON t1.id + 1 = t2.id WHERE t2.id IS NULL'
            cursor.execute(query)
            result = cursor.fetchone()
            next_id = result[0] if result[0] is not None else 1

            query = 'INSERT INTO users (id, username, password, role) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (next_id, usernameEntry.get(), passwordEntry.get(), roleEntry.get()))
            con.commit()
            messagebox.showinfo('Success', 'User added successfully', parent=userWindow)
            show_users()
        except:
            messagebox.showerror('Error', 'Username already exists', parent=userWindow)

    def delete_user():
        selected_item = userTable.focus()
        if not selected_item:
            messagebox.showerror('Error', 'Please select a user to delete', parent=userWindow)
            return

        content = userTable.item(selected_item)
        user_id = content['values'][0]

        if user_id == 1:
            messagebox.showerror('Error', 'Cannot delete the default admin user', parent=userWindow)
            return

        if messagebox.askyesno('Confirm', 'Are you sure you want to delete this user?', parent=userWindow):
            query = 'DELETE FROM users WHERE id=%s'
            cursor.execute(query, user_id)
            con.commit()
            show_users()

    def show_users():
        query = 'SELECT id, username, role FROM users'
        cursor.execute(query)
        users = cursor.fetchall()
        userTable.delete(*userTable.get_children())
        for user in users:
            userTable.insert('', END, values=user)

    userWindow = Toplevel()
    userWindow.grab_set()
    userWindow.geometry("600x400+500+250")
    userWindow.title("User Management")
    userWindow.resizable(False, False)

    formFrame = Frame(userWindow)
    formFrame.pack(pady=20)

    usernameLabel = Label(formFrame, text="Username:", font=("Arial", 15))
    usernameLabel.grid(row=0, column=0, padx=10, pady=5)
    usernameEntry = Entry(formFrame, font=("Arial", 15))
    usernameEntry.grid(row=0, column=1, padx=10, pady=5)

    passwordLabel = Label(formFrame, text="Password:", font=("Arial", 15))
    passwordLabel.grid(row=1, column=0, padx=10, pady=5)
    passwordEntry = Entry(formFrame, font=("Arial", 15), show='*')
    passwordEntry.grid(row=1, column=1, padx=10, pady=5)

    roleLabel = Label(formFrame, text="Role:", font=("Arial", 15))
    roleLabel.grid(row=2, column=0, padx=10, pady=5)
    roleEntry = ttk.Combobox(formFrame, font=("Arial", 15), values=('admin', 'teacher'), state='readonly')
    roleEntry.grid(row=2, column=1, padx=10, pady=5)

    addButton = ttk.Button(formFrame, text="Add User", command=add_user)
    addButton.grid(row=3, column=0, pady=10)

    deleteButton = ttk.Button(formFrame, text="Delete User", command=delete_user)
    deleteButton.grid(row=3, column=1, pady=10)

    tableFrame = Frame(userWindow)
    tableFrame.pack(pady=20)

    scrollbarX = Scrollbar(tableFrame, orient=HORIZONTAL)
    scrollbarY = Scrollbar(tableFrame, orient=VERTICAL)

    userTable = ttk.Treeview(tableFrame, columns=('ID', 'Username', 'Role'), xscrollcommand=scrollbarX.set, yscrollcommand=scrollbarY.set)

    scrollbarX.config(command=userTable.xview)
    scrollbarY.config(command=userTable.yview)

    userTable.heading('ID', text='ID')
    userTable.heading('Username', text='Username')
    userTable.heading('Role', text='Role')

    userTable.config(show='headings')

    userTable.column('ID', width=100, anchor='center')
    userTable.column('Username', width=200, anchor='center')
    userTable.column('Role', width=100, anchor='center')

    userTable.pack(fill=BOTH, expand=True)
    scrollbarX.pack(side=BOTTOM, fill=X)
    scrollbarY.pack(side=RIGHT, fill=Y)

    show_users()


def enable_buttons_based_on_role():
    addButton.config(state=DISABLED)
    searchButton.config(state=DISABLED)
    deleteButton.config(state=DISABLED)
    updateButton.config(state=DISABLED)
    showButton.config(state=DISABLED)
    exportButton.config(state=DISABLED)
    manageUsersButton.config(state=DISABLED)
    attendanceButton.grid_remove()

    if current_role == 'admin':
        addButton.config(state=NORMAL)
        searchButton.config(state=NORMAL)
        deleteButton.config(state=NORMAL)
        updateButton.config(state=NORMAL)
        showButton.config(state=NORMAL)
        exportButton.config(state=NORMAL)
        manageUsersButton.config(state=NORMAL)
    elif current_role == 'teacher':
        searchButton.config(state=NORMAL)
        showButton.config(state=NORMAL)
        exportButton.config(state=NORMAL)
        attendanceButton.grid(row=6, column=0, pady=20)

    switchUserButton.grid(row=9, column=0, pady=20)

    if current_user:
        titleLabel.config(text=f"Student Management System - {current_role.capitalize()}: {current_user}")
    else:
        titleLabel.config(text="Student Management System")


def logout():
    global current_user, current_role
    current_user = None
    current_role = None
    enable_buttons_based_on_role()
    show_login_window()


def show_qr_code():
    qr_window = Toplevel()
    qr_window.grab_set()
    qr_window.geometry("400x500+500+300")
    qr_window.title("Your QR Code")
    qr_window.resizable(False, False)

    qr_path = generate_qr_code(current_user)

    qr_image = PhotoImage(file=qr_path)
    qr_label = Label(qr_window, image=qr_image)
    qr_label.image = qr_image
    qr_label.pack(pady=20)

    instructions = Label(qr_window, text="Show the QR code to the camera for attendance", font=("Arial", 12))
    instructions.pack(pady=10)


def mark_attendance():
    if current_role != 'teacher':
        messagebox.showerror('Error', 'Only teachers can mark attendance')
        return

    def check_attendance():
        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 450)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        while True:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (450, 300))
            qr_info = decode(frame)

            if len(qr_info) > 0:
                qr = qr_info[0]
                data = qr.data
                rect = qr.rect
                polygon = qr.polygon

                query = "SELECT name, surname FROM students WHERE id = %s"
                cursor.execute(query, data.decode())
                student_info = cursor.fetchone()

                if student_info:
                    student_name = f"{student_info[0]} {student_info[1]}"
                    cv2.putText(frame, f'STUDENT: {student_name}', (rect.left, rect.top - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    frame = cv2.rectangle(frame, (rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height), (0, 255, 0), 5)
                    frame = cv2.polylines(frame, [np.array(polygon)], True, (255, 0, 0), 5)
                    cv2.imshow("Attendance Scanner", frame)
                    cv2.waitKey(1000)

                    if data.decode() not in most_recent_access.keys() or time.time() - most_recent_access[data.decode()] > time_between_logs_th:
                        most_recent_access[data.decode()] = time.time()
                        with open(attendance_log_path, 'a') as f:
                            f.write(f'{data.decode()}, {student_name}, {datetime.datetime.now()}\n')
                            f.close()

                        messagebox.showinfo('Success', f'Attendance marked for {student_name}!')
                        break
                else:
                    cv2.putText(frame, 'ACCESS DENIED', (rect.left, rect.top - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    frame = cv2.rectangle(frame, (rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height), (0, 0, 255), 5)
                    frame = cv2.polylines(frame, [np.array(polygon)], True, (255, 0, 0), 5)

            cv2.imshow('Attendance Scanner', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    attendance_window = Toplevel()
    attendance_window.grab_set()
    attendance_window.geometry("400x300+500+300")
    attendance_window.title("Mark Attendance")
    attendance_window.resizable(False, False)

    message = Label(attendance_window, text="Show student QR code to mark attendance\nPress 'q' to quit camera", font=("Arial", 12))
    message.pack(pady=20)

    start_button = ttk.Button(attendance_window, text="Start Camera", command=check_attendance)
    start_button.pack(pady=20)


window = ttkthemes.ThemedTk()
window.set_theme("clam")
window.geometry("3020x1960+0+0")
window.title("Student Management System")

dateLabel = Label(window, font=('Open Sans', 18, 'bold'))
dateLabel.place(x=5, y=15)
date()
titleLabel = Label(window, font=('Open Sans', 32, 'bold'))
titleLabel.place(x=500, y=20)
titleLabel.config(text="Student Management System")

dbButton = ttk.Button(window, text="Connect to Database", command=connect_db)
dbButton.place(x=1300, y=25)

leftSide = Frame(window)
leftSide.place(x=50, y=100, width=300, height=700)

image = PhotoImage(file='image.png')
image_label = Label(leftSide, image=image)
image_label.grid(row=0, column=0)

addButton = ttk.Button(leftSide, text="Add Student", width=15, state=DISABLED, command=lambda: toplevel_data('Add Student', 'ADD STUDENT', add_data))
addButton.grid(row=1, column=0, pady=20)

searchButton = ttk.Button(leftSide, text="Search Student", state=DISABLED, width=15, command=lambda: toplevel_data('Search Student', 'SEARCH STUDENT', search_data))
searchButton.grid(row=2, column=0, pady=20)

deleteButton = ttk.Button(leftSide, text="Delete Student", state=DISABLED, width=15, command=delete_student)
deleteButton.grid(row=3, column=0, pady=20)

updateButton = ttk.Button(leftSide, text="Update Student", state=DISABLED, width=15, command=lambda: toplevel_data('Update Student', 'UPDATE STUDENT', update_data))
updateButton.grid(row=4, column=0, pady=20)

showButton = ttk.Button(leftSide, text="Show Students", state=DISABLED, width=15, command=show_student)
showButton.grid(row=5, column=0, pady=20)

exportButton = ttk.Button(leftSide, text="Export Data", state=DISABLED, width=15, command=export_data)
exportButton.grid(row=6, column=0, pady=20)

exitButton = ttk.Button(leftSide, text="Exit", width=15, command=exit)
exitButton.grid(row=7, column=0, pady=20)

manageUsersButton = ttk.Button(leftSide, text="Manage Users", state=DISABLED, width=15, command=manage_users)
manageUsersButton.grid(row=8, column=0, pady=20)

switchUserButton = ttk.Button(leftSide, text="Switch User", width=15, command=logout)
switchUserButton.grid(row=9, column=0, pady=20)

attendanceButton = ttk.Button(leftSide, text="Mark Attendance", width=15, command=mark_attendance)
attendanceButton.grid(row=10, column=0, pady=20)

rightSide = Frame(window)
rightSide.place(x=300, y=100, width=1200, height=700)

scrollbarX = Scrollbar(rightSide, orient=HORIZONTAL)
scrollbarY = Scrollbar(rightSide, orient=VERTICAL)

scrollbarX.pack(side=BOTTOM, fill=X)
scrollbarY.pack(side=RIGHT, fill=Y)

studentTable = ttk.Treeview(rightSide, columns=('ID', 'Name', 'Surname', 'Mobile Number', 'Gender', 'Date of Birth', 'Email', 'Program', 'Added Date', 'Added Time'), xscrollcommand=scrollbarX.set, yscrollcommand=scrollbarY.set)
scrollbarX.config(command=studentTable.xview)
scrollbarY.config(command=studentTable.yview)

studentTable.pack(fill=BOTH, expand=True)

studentTable.heading('ID', text='ID')
studentTable.heading('Name', text='Name')
studentTable.heading('Surname', text='Surname')
studentTable.heading('Mobile Number', text='Mobile Number')
studentTable.heading('Gender', text='Gender')
studentTable.heading('Date of Birth', text='Date of Birth')
studentTable.heading('Email', text='Email')
studentTable.heading('Program', text='Program')
studentTable.heading('Added Date', text='Added Date')
studentTable.heading('Added Time', text='Added Time')

studentTable.config(show='headings')

studentTable.column('ID', width=100, anchor='center')
studentTable.column('Name', width=200, anchor='center')
studentTable.column('Surname', width=200, anchor='center')
studentTable.column('Mobile Number', width=150, anchor='center')
studentTable.column('Gender', width=150, anchor='center')
studentTable.column('Date of Birth', width=150, anchor='center')
studentTable.column('Email', width=300, anchor='center')
studentTable.column('Program', width=300, anchor='center')
studentTable.column('Added Date', width=150, anchor='center')
studentTable.column('Added Time', width=150, anchor='center')

ttk.Style().configure("Treeview", rowheight=30, background='floral white', fieldbackground='floral white')
ttk.Style().configure("Treeview.Heading", foreground='red4', font=('Open Sans', 14, 'bold'))

window.mainloop()