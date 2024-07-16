import sys
import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from datetime import datetime
from os.path import join

try:
    from pony.orm import *
except ImportError:
    print("Pony ORM tidak ditemukan. Pastikan Anda telah menginstalnya dengan 'pip install pony'.")
    sys.exit(1)

db = Database()

class Attendance(db.Entity):
    id = PrimaryKey(int, auto=True)
    student_name = Required(str)
    student_nim = Required(str)
    student_faculty = Required(str)
    attendance_status = Required(str)
    timestamp = Required(datetime)

class AttendanceApp(toga.App):
    def startup(self):
        # Tentukan lokasi database berdasarkan platform
        if sys.platform == 'android':
            database_path = join(self.paths.data, 'attendance.sqlite')
        else:
            database_path = 'C:\\Users\\Lenovo\\AplikasiAbsensi\\src\\AplikasiAbsensi\\attendance.sqlite'

        # Menghubungkan ke database SQLite
        try:
            db.bind(provider='sqlite', filename=database_path, create_db=True)
            db.generate_mapping(create_tables=True)
        except Exception as e:
            print(f"Error saat menghubungkan ke database: {e}")
            sys.exit(1)

        self.main_window = toga.MainWindow(title=self.formal_name)

        label_style = Pack(padding=(0, 5), font_weight='bold', color='#2C3E50', font_size=14)
        input_style = Pack(flex=1, padding=5, font_size=14, background_color='#ECF0F1', color='#34495E')

        self.student_name_input = toga.TextInput(style=input_style, on_change=self.check_inputs)
        self.student_nim_input = toga.TextInput(style=input_style, on_change=self.check_inputs)
        self.student_faculty_input = toga.TextInput(style=input_style, on_change=self.check_inputs)

        self.attendance_options = ['Hadir', 'Tidak Hadir', 'Izin', 'Sakit']
        self.attendance_select = toga.Selection(
            items=self.attendance_options, 
            style=Pack(flex=1, padding=5, font_size=14, color='#34495E', background_color='#ECF0F1'),
            on_change=self.check_inputs
        )

        button_style = Pack(padding=10, font_size=16, font_weight='bold', background_color='#3498DB', color='white')
        self.attendance_button = toga.Button('Absensi', on_press=self.add_student, style=button_style)
        self.attendance_button.enabled = False

        input_box = toga.Box(
            children=[
                toga.Label('Nama Mahasiswa:', style=label_style), self.student_name_input,
                toga.Label('NIM:', style=label_style), self.student_nim_input,
                toga.Label('Fakultas:', style=label_style), self.student_faculty_input,
                toga.Label('Kehadiran:', style=label_style), self.attendance_select,
                self.attendance_button
            ],
            style=Pack(direction=COLUMN, padding=20, background_color='#F9FAFB')
        )

        self.attendance_list_box = toga.ScrollContainer(style=Pack(flex=1))

        main_box = toga.Box(
            children=[input_box, self.attendance_list_box],
            style=Pack(direction=COLUMN)
        )

        self.main_window.content = main_box
        self.main_window.show()
        self.update_attendance_list()

    def check_inputs(self, widget):
        self.attendance_button.enabled = all([
            self.student_name_input.value,
            self.student_nim_input.value,
            self.student_faculty_input.value,
            self.attendance_select.value
        ])
        self.attendance_button.style.background_color = '#2ECC71' if self.attendance_button.enabled else '#3498DB'

    @db_session
    def add_student(self, widget):
        try:
            Attendance(
                student_name=self.student_name_input.value,
                student_nim=self.student_nim_input.value,
                student_faculty=self.student_faculty_input.value,
                attendance_status=self.attendance_select.value,
                timestamp=datetime.now()
            )
            commit()  # Pastikan data tersimpan
            self.student_name_input.value = ''
            self.student_nim_input.value = ''
            self.student_faculty_input.value = ''
            self.attendance_select.value = self.attendance_options[0]
            self.attendance_button.enabled = False
            self.attendance_button.style.background_color = '#3498DB'
            self.update_attendance_list()
        except Exception as e:
            print(f"Error saat menambahkan data absensi: {e}")

    @db_session
    def update_attendance_list(self):
        list_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        attendances = select(a for a in Attendance).order_by(desc(Attendance.timestamp))[:50]

        for index, attendance in enumerate(attendances):
            bg_color = '#E8F6F3' if index % 2 == 0 else '#F4F6F7'
            attendance_box = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color=bg_color))
            attendance_box.add(
                toga.Label(
                    f'{attendance.student_name} (NIM: {attendance.student_nim})',
                    style=Pack(font_weight='bold', font_size=14, color='#2C3E50')
                )
            )
            attendance_box.add(toga.Label(f'Fakultas: {attendance.student_faculty}', style=Pack(font_size=12, color='#34495E')))
            attendance_box.add(toga.Label(f'Status: {attendance.attendance_status}', style=Pack(font_size=12, color='#34495E')))
            attendance_box.add(toga.Label(f'Waktu: {attendance.timestamp.strftime("%Y-%m-%d %H:%M:%S")}', style=Pack(font_size=10, color='#7F8C8D')))
            list_box.add(attendance_box)

        self.attendance_list_box.content = list_box

def main():
    return AttendanceApp('Aplikasi Absensi Mahasiswa', 'org.beeware.attendance')

if __name__ == '__main__':
    main().main_loop()
