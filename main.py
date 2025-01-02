import sys
from idlelib.help_about import AboutDialog
from PyQt6.QtCore import QSize
import sqlite3
from PyQt6.QtGui import QAction, QIcon ,QGuiApplication
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox


class DatabaseConnection():
    def __init__(self,database_file = "database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Dynamically set window size based on screen dimensions
        screen = QGuiApplication.primaryScreen()#This retrieves the primary screen of the device where the application is running.
        screen_geometry = screen.availableGeometry()
        width = screen_geometry.width() * 0.6  # 60% of screen width
        height = screen_geometry.height() * 0.6  # 60% of screen height
        self.resize(int(width), int(height))

        file_menu_item = self.menuBar().addMenu("&File")#self.menu bar is a function of parent class and addmenu also
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"),"Add Student",self)#action will be on when icon representing add student is pressed,see line 55
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)#an icon will also be shown if systemm allows,at the side of add student option

        about_action = QAction("About",self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"),"Search",self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Roll.no","Name","Course","Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        #create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        #create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)
        del_button = QPushButton("Delete Record")
        del_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(del_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number,row_data in enumerate(result):
            self.table.insertRow(row_number)
            print(row_data)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number,column_number,QTableWidgetItem(str(data)))
        connection.close()

    #add reset button after searching the record
    def add_reset_button(self):
        self.reset_button = QPushButton("Reset Table")
        self.reset_button.clicked.connect(self.remove_reset_button)
        self.statusbar.addWidget(self.reset_button)

    def remove_reset_button(self):
        self.load_data()
        self.statusbar.removeWidget(self.reset_button)

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        searching = SearchStudent()
        searching.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content ="""
        <p style="text-align: center; font-size: 14px;">
        This app was created during the Python Mega Course.<br>
        Feel free to use the app again!
        </p>
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = age_calculator.table.currentRow()
        student_name = age_calculator.table.item(index,1).text()
        self.roll_no2 = age_calculator.table.item(index,0).text()
        subject = age_calculator.table.item(index,2).text()
        ph_no = age_calculator.table.item(index,3).text()

        #add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name of student")
        layout.addWidget(self.student_name)

        #add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology","Math","Astronomy","Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(subject)
        layout.addWidget(self.course_name)

        #add mobile
        self.student_mobile = QLineEdit(ph_no)
        self.student_mobile.setPlaceholderText("mobile.no of Student")
        layout.addWidget(self.student_mobile)

        #add roll.no
        self.roll_no = QLineEdit(self.roll_no2)
        self.roll_no.setPlaceholderText("Enter the roll.no")
        layout.addWidget(self.roll_no)

        #add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.update_st)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_st(self):
        name = self.student_name.text()
        mobile = self.student_mobile.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        rollno = self.roll_no.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET id = ? ,name = ? , course = ?,mobile = ? WHERE id = ?",
                       (rollno,name,course,mobile,self.roll_no2))
        connection.commit()
        #refresh the table
        age_calculator.load_data()
        # Close the dialog after successful update
        self.accept()
        cursor.close()
        connection.close()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")


        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to Delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.reject) #The reject() method is a built-in function in QDialog that closes the dialog without indicating a positive response.

    def delete_student(self):
        #get row index and student id
        index = age_calculator.table.currentRow()
        roll_no = age_calculator.table.item(index,0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (roll_no,))

        connection.commit()
        cursor.close()
        connection.close()
        age_calculator.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The Record was deleted successfully")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name of student")
        layout.addWidget(self.student_name)

        #add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology","Math","Astronomy","Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #add mobile
        self.student_mobile = QLineEdit()
        self.student_mobile.setPlaceholderText("mobile.no of Student")
        layout.addWidget(self.student_mobile)

        #add roll.no
        self.roll_no = QLineEdit()
        self.roll_no.setPlaceholderText("Enter the roll.no")
        layout.addWidget(self.roll_no)

        #add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        mobile = self.student_mobile.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        rollno = self.roll_no.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (id,name,course,mobile) VALUES (?,?,?,?)",
                       (rollno,name,course,mobile))
        connection.commit()
        cursor.close()
        connection.close()
        age_calculator.load_data()

class SearchStudent(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        #add search window
        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText("Enter Student's Name or Roll.no")
        layout.addWidget(self.name_search)

        #add search button
        self.search_button = QPushButton("Get Details")
        self.search_button.clicked.connect(self.searching_student)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def searching_student(self):
        input = self.name_search.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id LIKE ? OR name LIKE ?",
                       (f"%{input}%", f"%{input}%"))
        results = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Clear the current table contents
        age_calculator.table.setRowCount(0)

        # Populate the table with search results
        for row_number, row_data in enumerate(results):
            age_calculator.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                age_calculator.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        # Highlight matching rows (optional)
        for row_number in range(len(results)):
            for column_number in range(age_calculator.table.columnCount()-2):
                age_calculator.table.item(row_number, column_number).setSelected(True)

        #calling method to reset the table
        age_calculator.add_reset_button()



app=QApplication(sys.argv)
age_calculator = MainWindow()
age_calculator.show()
age_calculator.load_data()
sys.exit(app.exec())