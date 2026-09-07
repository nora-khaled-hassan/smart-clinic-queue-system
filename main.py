
import json
import re
from datetime import datetime, timedelta


class Person:
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone

    def get_info(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone
        }


class Patient(Person):
    def __init__(
        self,
        user_id,
        name,
        age,
        phone,
        case_type=None,
        priority=None,
        appointments=None
    ):
        super().__init__(user_id, name, phone)
        self.age = age
        self.case_type = case_type
        self.priority = priority
        self.appointments = appointments if appointments else []

    def get_info(self):
        data = super().get_info()
        data.update({
            "age": self.age,
            "case_type": self.case_type,
            "priority": self.priority,
            "appointments": self.appointments
        })
        return data


class Doctor(Person):
    def __init__(
        self,
        user_id,
        name,
        specialty,
        phone,
        rate,
        appointment_duration=30,
        working_days=None,
        working_hours=None,
        availability=True,
        assigned_nurses=None
    ):
        super().__init__(user_id, name, phone)
        self.specialty = specialty
        self.rate = rate
        self.appointment_duration = appointment_duration
        self.working_days = working_days if working_days else []
        self.working_hours = working_hours if working_hours else {}
        self.availability = availability
        self.assigned_nurses = assigned_nurses if assigned_nurses else []

    def get_info(self):
        data = super().get_info()
        data.update({
            "specialty": self.specialty,
            "rate": self.rate,
            "appointment_duration": self.appointment_duration,
            "working_days": self.working_days,
            "working_hours": self.working_hours,
            "availability": self.availability,
            "assigned_nurses": self.assigned_nurses
        })
        return data


class Nurse(Person):
    def __init__(
        self,
        user_id,
        name,
        phone,
        assigned_doctors=None,
        availability=True
    ):
        super().__init__(user_id, name, phone)
        self.assigned_doctors = assigned_doctors if assigned_doctors else []
        self.availability = availability

    def get_info(self):
        data = super().get_info()
        data.update({
            "assigned_doctors": self.assigned_doctors,
            "availability": self.availability
        })
        return data


class UserAccount:
    def __init__(self, user_id, name, phone, role, password):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.role = role
        self.password = password

    def get_data(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "role": self.role,
            "password": self.password
        }


class ClinicSystem:

    def __init__(self, file_name="clinic_data.json"):
        self.file_name = file_name

        self.users = []
        self.patients = []
        self.doctors = []
        self.nurses = []
        self.appointments = []
        self.visits = []
        self.bills = []
        self.payments = []
        self.waiting_queue = []
        self.action_history = []

        self.settings = {
            "service_rates": {
                "consultation": 2.5,
                "examination": 3.75,
                "emergency": 6.75
            },
            "case_priority": {
                "emergency": 1,
                "urgent": 2,
                "regular": 3
            }
        }

        self.current_user = None

        self.load_data()
        self.create_default_admin()

    def load_data(self):
        try:
            with open(self.file_name, "r") as file:
                data = json.load(file)

            self.users = data.get("users", [])
            self.patients = data.get("patients", [])
            self.doctors = data.get("doctors", [])
            self.nurses = data.get("nurses", [])
            self.appointments = data.get("appointments", [])
            self.visits = data.get("visits", [])
            self.bills = data.get("bills", [])
            self.payments = data.get("payments", [])
            self.waiting_queue = data.get("waiting_queue", [])
            self.action_history = data.get("action_history", [])

            self.settings = data.get("settings", self.settings)

            for doctor in self.doctors:
                if "appointment_duration" not in doctor:
                    doctor["appointment_duration"] = 30

        except FileNotFoundError:
            self.save_data()

        except json.JSONDecodeError:
            print("Error: JSON file is not valid.")
            self.save_data()

    def save_data(self):
        data = {
            "users": self.users,
            "patients": self.patients,
            "doctors": self.doctors,
            "nurses": self.nurses,
            "appointments": self.appointments,
            "visits": self.visits,
            "bills": self.bills,
            "payments": self.payments,
            "waiting_queue": self.waiting_queue,
            "action_history": self.action_history,
            "settings": self.settings
        }

        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=4)

    def create_default_admin(self):
        for user in self.users:
            if user["user_id"] == "A001":
                return

        admin = {
            "user_id": "A001",
            "name": "Clinic Admin",
            "phone": "01000000000",
            "role": "admin",
            "password": "admin123"
        }

        self.users.append(admin)
        self.save_data()

    def valid_id(self, user_id, role):
        patterns = {
            "patient": r"^P\d{3}$",
            "doctor": r"^D\d{3}$",
            "nurse": r"^N\d{3}$",
            "admin": r"^A\d{3}$"
        }

        return re.fullmatch(patterns[role], user_id) is not None

    def valid_phone(self, phone):
        return re.fullmatch(r"01[0125]\d{8}", phone) is not None

    def id_exists(self, user_id):
        for user in self.users:
            if user["user_id"] == user_id:
                return True

        return False

    def find_user(self, user_id):
        for user in self.users:
            if user["user_id"] == user_id:
                return user

        return None

    def find_patient(self, patient_id):
        for patient in self.patients:
            if patient["patient_id"] == patient_id:
                return patient

        return None

    def find_doctor(self, doctor_id):
        for doctor in self.doctors:
            if doctor["doctor_id"] == doctor_id:
                return doctor

        return None

    def find_nurse(self, nurse_id):
        for nurse in self.nurses:
            if nurse["nurse_id"] == nurse_id:
                return nurse

        return None

    def register_patient(self):
        print("\n========== PATIENT REGISTRATION ==========")

        name = input("Name: ").strip()
        while not name:
            print("Name cannot be empty.")
            name = input("Name: ").strip()

        while True:
            phone = input("Phone: ").strip()
            if self.valid_phone(phone):
                break
            print("Invalid phone number.")

        while True:
            try:
                age = int(input("Age: "))
                if 0 < age <= 120:
                    break
                print("Invalid age.")
            except ValueError:
                print("Age must be a number.")

        password = input("Password: ").strip()
        while len(password) < 4:
            print("Password must contain at least 4 characters.")
            password = input("Password: ").strip()

        patient_id = self.generate_patient_id()

        self.users.append({
            "user_id": patient_id,
            "name": name,
            "phone": phone,
            "role": "patient",
            "password": password
        })

        self.patients.append({
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "phone": phone,
            "case_type": None,
            "priority": None,
            "appointments": []
        })

        self.action_history.append(f"Patient {patient_id} registered.")
        self.save_data()

        print("\nPatient registered successfully.")
        print(f"Patient ID: {patient_id}")

    def generate_patient_id(self):
        number = 1
        while True:
            patient_id = f"P{number:03d}"
            if not self.id_exists(patient_id):
                return patient_id
            number += 1

    def generate_doctor_id(self):
        number = 1

        while True:
            doctor_id = f"D{number:03d}"

            if not self.id_exists(doctor_id):
                return doctor_id

            number += 1

    def add_doctor(self):
        if not self.current_user or self.current_user["role"] != "admin":
            print("Access denied.")
            return

        print("\n========== ADD DOCTOR ==========")

        name = input("Doctor name: ").strip()

        while not name:
            print("Name cannot be empty.")
            name = input("Doctor name: ").strip()

        while True:
            phone = input("Phone: ").strip()

            if self.valid_phone(phone):
                break

            print("Invalid phone number.")

        specialty = input("Specialty: ").strip()

        while not specialty:
            print("Specialty cannot be empty.")
            specialty = input("Specialty: ").strip()

        while True:
            try:
                rate = float(input("Doctor rate: "))

                if rate <= 0:
                    print("Rate must be greater than zero.")
                    continue

                break

            except ValueError:
                print("Rate must be a number.")

        while True:
            try:
                duration = int(
                    input("Appointment duration in minutes: ")
                )

                if duration <= 0:
                    print("Duration must be greater than zero.")
                    continue

                break

            except ValueError:
                print("Duration must be a number.")

        print("\nAvailable working days:")

        days = [
            "Saturday",
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ]

        for i, day in enumerate(days, 1):
            print(f"{i}. {day}")

        while True:
            selected = input(
                "Enter 3 day numbers separated by comma: "
            )

            try:
                numbers = [
                    int(x.strip())
                    for x in selected.split(",")
                ]

                if len(numbers) != 3:
                    print("Doctor must work exactly 3 days.")
                    continue

                if len(set(numbers)) != 3:
                    print("You cannot choose the same day twice.")
                    continue

                if any(x < 1 or x > 7 for x in numbers):
                    print("Invalid day.")
                    continue

                working_days = [
                    days[x - 1]
                    for x in numbers
                ]

                break

            except ValueError:
                print("Invalid day input.")

        while True:
            start = input("Starting time (HH:MM): ").strip()

            if re.fullmatch(
                r"^(?:[01]\d|2[0-3]):[0-5]\d$",
                start
            ):
                break

            print("Invalid starting time.")

        while True:
            end = input("Ending time (HH:MM): ").strip()

            if re.fullmatch(
                r"^(?:[01]\d|2[0-3]):[0-5]\d$",
                end
            ):
                break

            print("Invalid ending time.")

        password = input("Password: ").strip()

        while len(password) < 4:
            print("Password must contain at least 4 characters.")
            password = input("Password: ").strip()

        doctor_id = self.generate_doctor_id()

        user = {
            "user_id": doctor_id,
            "name": name,
            "phone": phone,
            "role": "doctor",
            "password": password
        }

        doctor = {
            "doctor_id": doctor_id,
            "name": name,
            "specialty": specialty,
            "phone": phone,
            "rate": rate,
            "appointment_duration": duration,
            "working_days": working_days,
            "working_hours": {
                "start": start,
                "end": end
            },
            "availability": True,
            "assigned_nurses": []
        }

        self.users.append(user)
        self.doctors.append(doctor)

        self.action_history.append(
            f"Doctor {doctor_id} added."
        )

        self.save_data()

        print("\nDoctor added successfully.")
        print(f"Doctor ID: {doctor_id}")

    def generate_nurse_id(self):
        number = 1

        while True:
            nurse_id = f"N{number:03d}"

            if not self.id_exists(nurse_id):
                return nurse_id

            number += 1

    def add_nurse(self):
        if not self.current_user or self.current_user["role"] != "admin":
            print("Access denied.")
            return

        print("\n========== ADD NURSE ==========")

        name = input("Nurse name: ").strip()

        while not name:
            print("Name cannot be empty.")
            name = input("Nurse name: ").strip()

        while True:
            phone = input("Phone: ").strip()

            if self.valid_phone(phone):
                break

            print("Invalid phone number.")

        while True:
            password = input("Password: ").strip()

            if len(password) >= 4:
                break

            print("Password must contain at least 4 characters.")

        if not self.doctors:
            print("No doctors available.")
            return

        print("\n========== AVAILABLE DOCTORS ==========")

        for doctor in self.doctors:
            print(
                f"{doctor['doctor_id']} | "
                f"{doctor['name']} | "
                f"{doctor['specialty']}"
            )

        while True:
            doctor_id = input(
                "\nEnter doctor ID: "
            ).strip().upper()

            doctor = self.find_doctor(doctor_id)

            if doctor:
                break

            print(
                "Doctor not found. "
                "Please enter a valid doctor ID."
            )

        nurse_id = self.generate_nurse_id()

        nurse = {
            "nurse_id": nurse_id,
            "name": name,
            "phone": phone,
            "assigned_doctors": [doctor_id],
            "availability": True
        }

        user = {
            "user_id": nurse_id,
            "name": name,
            "phone": phone,
            "role": "nurse",
            "password": password
        }

        self.users.append(user)
        self.nurses.append(nurse)

        doctor["assigned_nurses"].append(nurse_id)

        self.action_history.append(
            f"Nurse {nurse_id} added and assigned "
            f"to doctor {doctor_id}."
        )

        self.save_data()

        print("\nNurse added successfully.")
        print(f"Nurse ID: {nurse_id}")
        print(f"Assigned Doctor: {doctor_id}")

    def login(self):
        print("\n========== LOGIN ==========")

        user_id = input("ID: ").strip().upper()
        password = input("Password: ").strip()

        user = self.find_user(user_id)

        if user is None:
            print("User not found.")
            return False

        if user["password"] != password:
            print("Wrong password.")
            return False

        self.current_user = user

        print(f"\nWelcome, {user['name']}!")
        print(f"Role: {user['role'].upper()}")

        return True

    def logout(self):
        if self.current_user:
            print(f"Goodbye, {self.current_user['name']}.")

        self.current_user = None

    def show_profile(self):
        if not self.current_user:
            print("Please login first.")
            return

        user_id = self.current_user["user_id"]
        role = self.current_user["role"]

        print("\n========== PROFILE ==========")

        print(f"ID: {user_id}")
        print(f"Name: {self.current_user['name']}")
        print(f"Phone: {self.current_user['phone']}")
        print(f"Role: {role}")

        if role == "patient":
            patient = self.find_patient(user_id)

            if patient:
                print(f"Age: {patient['age']}")
                print(f"Case Type: {patient['case_type']}")
                print(f"Priority: {patient['priority']}")
                print(
                    f"Appointments: "
                    f"{len(patient['appointments'])}"
                )

        elif role == "doctor":
            doctor = self.find_doctor(user_id)

            if doctor:
                print(f"Specialty: {doctor['specialty']}")
                print(f"Rate: {doctor['rate']}")
                print(
                    f"Appointment Duration: "
                    f"{doctor.get('appointment_duration', 30)} minutes"
                )
                print(
                    f"Working Days: "
                    f"{', '.join(doctor['working_days'])}"
                )
                print(
                    f"Working Hours: "
                    f"{doctor['working_hours']['start']} - "
                    f"{doctor['working_hours']['end']}"
                )

        elif role == "nurse":
            nurse = self.find_nurse(user_id)

            if nurse:
                print(
                    f"Assigned Doctors: "
                    f"{', '.join(nurse['assigned_doctors']) if nurse['assigned_doctors'] else 'None'}"
                )

    def show_patients(self):
        print("\n========== PATIENTS ==========")

        if not self.patients:
            print("No patients found.")
            return

        for patient in self.patients:
            print(
                f"{patient['patient_id']} | "
                f"{patient['name']} | "
                f"Age: {patient['age']} | "
                f"Phone: {patient['phone']}"
            )

    def show_doctors(self):
        print("\n========== DOCTORS ==========")

        if not self.doctors:
            print("No doctors found.")
            return

        for doctor in self.doctors:
            print(
                f"{doctor['doctor_id']} | "
                f"{doctor['name']} | "
                f"{doctor['specialty']} | "
                f"Rate: {doctor['rate']} | "
                f"Duration: "
                f"{doctor.get('appointment_duration', 30)} min"
            )

    def show_nurses(self):
        print("\n========== NURSES ==========")

        if not self.nurses:
            print("No nurses found.")
            return

        for nurse in self.nurses:
            doctors = ", ".join(
                nurse["assigned_doctors"]
            )

            print(
                f"{nurse['nurse_id']} | "
                f"{nurse['name']} | "
                f"Doctors: "
                f"{doctors if doctors else 'None'}"
            )

    def show_specialties(self):
        specialties = []

        for doctor in self.doctors:
            if (
                doctor["availability"]
                and doctor["specialty"] not in specialties
            ):
                specialties.append(
                    doctor["specialty"]
                )

        print("\n========== SPECIALTIES ==========")

        for i, specialty in enumerate(
            specialties,
            1
        ):
            print(f"{i}. {specialty}")

        return specialties

    def is_doctor_working(self, doctor, date):
        try:
            day = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).strftime("%A")

            return day in doctor["working_days"]

        except ValueError:
            return False

    def doctor_load(self, doctor_id, date):
        count = 0

        for appointment in self.appointments:
            if (
                appointment["doctor_id"] == doctor_id
                and appointment["date"] == date
                and appointment["status"] != "CANCELLED"
            ):
                count += 1

        return count

    def recommend_doctors(self, specialty, date):
        doctors = []

        for doctor in self.doctors:
            if (
                doctor["specialty"].lower()
                == specialty.lower()
                and doctor["availability"]
                and self.is_doctor_working(
                    doctor,
                    date
                )
            ):
                load = self.doctor_load(
                    doctor["doctor_id"],
                    date
                )

                doctors.append({
                    "doctor": doctor,
                    "load": load
                })

        doctors.sort(
            key=lambda x: x["load"]
        )

        return doctors

    def get_available_slots(self, doctor, date):
        if not self.is_doctor_working(
            doctor,
            date
        ):
            return []

        try:
            start = datetime.strptime(
                doctor["working_hours"]["start"],
                "%H:%M"
            )

            end = datetime.strptime(
                doctor["working_hours"]["end"],
                "%H:%M"
            )

        except (KeyError, ValueError):
            return []

        duration = doctor.get(
            "appointment_duration",
            30
        )

        booked_times = []

        for appointment in self.appointments:
            if (
                appointment["doctor_id"]
                == doctor["doctor_id"]
                and appointment["date"]
                == date
                and appointment["status"]
                != "CANCELLED"
            ):
                booked_times.append(
                    appointment["time"]
                )

        slots = []

        current = start

        while (
            current
            + timedelta(minutes=duration)
            <= end
        ):
            time = current.strftime("%H:%M")

            if time not in booked_times:
                slots.append(time)

            current += timedelta(
                minutes=duration
            )

        return slots

    def book_appointment(self):
        if not self.current_user:
            print("Please login first.")
            return

        print("\n========== BOOK APPOINTMENT ==========")

        specialties = self.show_specialties()

        if not specialties:
            print("No doctors available.")
            return

        while True:
            try:
                choice = int(
                    input("Choose specialty: ")
                )

                if 1 <= choice <= len(specialties):
                    specialty = specialties[
                        choice - 1
                    ]
                    break

                print("Invalid choice.")

            except ValueError:
                print(
                    "Please enter a number."
                )

        while True:
            date = input(
                "Enter appointment date "
                "(YYYY-MM-DD): "
            ).strip()

            try:
                selected_date = datetime.strptime(
                    date,
                    "%Y-%m-%d"
                )

                if selected_date.date() < datetime.now().date():
                    print(
                        "You cannot book a past date."
                    )
                    continue

                break

            except ValueError:
                print("Invalid date.")

        doctors = self.recommend_doctors(
            specialty,
            date
        )

        if not doctors:
            print(
                "No available doctors for "
                "this specialty on this date."
            )
            return

        print(
            "\n========== RECOMMENDED DOCTOR =========="
        )

        recommended = doctors[0]["doctor"]

        print(
            f"Doctor: {recommended['name']}"
        )
        print(
            f"Doctor ID: "
            f"{recommended['doctor_id']}"
        )
        print(
            f"Specialty: "
            f"{recommended['specialty']}"
        )
        print(
            f"Current Load: "
            f"{doctors[0]['load']}"
        )
        print(
            f"Appointment Duration: "
            f"{recommended.get('appointment_duration', 30)} "
            f"minutes"
        )

        print("\n1. Choose recommended doctor")
        print("2. Show all doctors")
        print("3. Cancel")

        while True:
            choice = input("Choose: ").strip()

            if choice == "1":
                doctor = recommended
                break

            elif choice == "2":
                print(
                    "\n========== ALL AVAILABLE DOCTORS =========="
                )

                for i, item in enumerate(
                    doctors,
                    1
                ):
                    d = item["doctor"]

                    print(
                        f"{i}. "
                        f"{d['doctor_id']} | "
                        f"{d['name']} | "
                        f"Load: {item['load']} | "
                        f"Duration: "
                        f"{d.get('appointment_duration', 30)} min"
                    )

                while True:
                    try:
                        doctor_choice = int(
                            input(
                                "Choose doctor: "
                            )
                        )

                        if (
                            1
                            <= doctor_choice
                            <= len(doctors)
                        ):
                            doctor = doctors[
                                doctor_choice - 1
                            ]["doctor"]
                            break

                        print(
                            "Invalid choice."
                        )

                    except ValueError:
                        print(
                            "Please enter a number."
                        )

                break

            elif choice == "3":
                return

            else:
                print("Invalid choice.")

        slots = self.get_available_slots(
            doctor,
            date
        )

        if not slots:
            print(
                "No available time slots "
                "for this doctor."
            )
            return

        print(
            f"\n========== AVAILABLE TIMES "
            f"FOR {doctor['name']} =========="
        )

        for i, slot in enumerate(
            slots,
            1
        ):
            print(
                f"{i}. {slot}"
            )

        while True:
            try:
                time_choice = int(
                    input("Choose time: ")
                )

                if (
                    1
                    <= time_choice
                    <= len(slots)
                ):
                    time = slots[
                        time_choice - 1
                    ]
                    break

                print("Invalid choice.")

            except ValueError:
                print(
                    "Please enter a number."
                )

        appointment_id = (
            f"AP{len(self.appointments) + 1:03d}"
        )

        appointment = {
            "appointment_id": appointment_id,
            "patient_id": self.current_user[
                "user_id"
            ],
            "doctor_id": doctor[
                "doctor_id"
            ],
            "date": date,
            "time": time,
            "status": "BOOKED",
            "case_type": None,
            "priority": None,
            "payment_status": "UNPAID"
        }

        self.appointments.append(
            appointment
        )

        patient = self.find_patient(
            self.current_user["user_id"]
        )

        if patient:
            patient["appointments"].append(
                appointment_id
            )

        self.action_history.append(
            f"Appointment {appointment_id} "
            f"booked."
        )

        self.save_data()

        print(
            "\nAppointment booked successfully."
        )
        print(
            f"Appointment ID: "
            f"{appointment_id}"
        )
        print(
            f"Doctor: {doctor['name']}"
        )
        print(
            f"Specialty: "
            f"{doctor['specialty']}"
        )
        print(
            f"Date: {date}"
        )
        print(
            f"Time: {time}"
        )

    def show_patient_appointments(self):
        if not self.current_user:
            return

        patient_id = self.current_user[
            "user_id"
        ]

        print(
            "\n========== MY APPOINTMENTS =========="
        )

        found = False

        for appointment in self.appointments:

            if (
                appointment["patient_id"]
                == patient_id
            ):

                found = True

                doctor = self.find_doctor(
                    appointment["doctor_id"]
                )

                doctor_name = (
                    doctor["name"]
                    if doctor
                    else appointment["doctor_id"]
                )

                print(
                    f"{appointment['appointment_id']} | "
                    f"Doctor: {doctor_name} | "
                    f"Date: {appointment['date']} | "
                    f"Time: {appointment['time']} | "
                    f"Status: {appointment['status']}"
                )

        if not found:
            print(
                "No appointments found."
            )

    def show_doctor_appointments(self):
        if not self.current_user:
            return

        doctor_id = self.current_user[
            "user_id"
        ]

        print(
            "\n========== MY APPOINTMENTS =========="
        )

        found = False

        for appointment in self.appointments:

            if (
                appointment["doctor_id"]
                == doctor_id
            ):

                found = True

                print(
                    f"{appointment['appointment_id']} | "
                    f"Patient: "
                    f"{appointment['patient_id']} | "
                    f"Date: {appointment['date']} | "
                    f"Time: {appointment['time']} | "
                    f"Status: {appointment['status']}"
                )

        if not found:
            print(
                "No appointments found."
            )

    def show_my_doctors(self):
        nurse = self.find_nurse(self.current_user["user_id"])

        if not nurse:
            print("Nurse not found.")
            return

        print("\n========== MY DOCTORS ==========")

        if not nurse["assigned_doctors"]:
            print("No doctors assigned.")
            return

        for doctor_id in nurse["assigned_doctors"]:
            doctor = self.find_doctor(doctor_id)

            if not doctor:
                continue

            print(f"\n{doctor['doctor_id']} | {doctor['name']} | {doctor['specialty']}")

            appointments = [
                a for a in self.appointments
                if a["doctor_id"] == doctor_id
            ]

            if not appointments:
                print("No appointments.")
                continue

            print("Appointments:")
            for a in appointments:
                patient = self.find_patient(a["patient_id"])
                name = patient["name"] if patient else a["patient_id"]
                print(
                    f"{a['appointment_id']} | {name} | "
                    f"{a['date']} | {a['time']} | "
                    f"{a['status']} | {a['payment_status']}"
                )

    def admin_menu(self):
        while (
            self.current_user
            and self.current_user["role"]
            == "admin"
        ):

            print(
                "\n========== ADMIN MENU =========="
            )
            print("1. Add Doctor")
            print("2. Add Nurse")
            print("3. Show Patients")
            print("4. Show Doctors")
            print("5. Show Nurses")
            print("6. Show Profile")
            print("7. Logout")

            choice = input(
                "Choose: "
            ).strip()

            if choice == "1":
                self.add_doctor()

            elif choice == "2":
                self.add_nurse()

            elif choice == "3":
                self.show_patients()

            elif choice == "4":
                self.show_doctors()

            elif choice == "5":
                self.show_nurses()

            elif choice == "6":
                self.show_profile()

            elif choice == "7":
                self.logout()

            else:
                print(
                    "Invalid choice."
                )

    def patient_menu(self):
        while (
            self.current_user
            and self.current_user["role"]
            == "patient"
        ):

            print(
                "\n========== PATIENT MENU =========="
            )
            print("1. Book Appointment")
            print("2. Show Profile")
            print("3. Show My Appointments")
            print("4. Logout")

            choice = input(
                "Choose: "
            ).strip()

            if choice == "1":
                self.book_appointment()

            elif choice == "2":
                self.show_profile()

            elif choice == "3":
                self.show_patient_appointments()

            elif choice == "4":
                self.logout()

            else:
                print(
                    "Invalid choice."
                )

    def doctor_menu(self):
        while (
            self.current_user
            and self.current_user["role"]
            == "doctor"
        ):

            print(
                "\n========== DOCTOR MENU =========="
            )
            print("1. Show Profile")
            print("2. Show My Appointments")
            print("3. Logout")

            choice = input(
                "Choose: "
            ).strip()

            if choice == "1":
                self.show_profile()

            elif choice == "2":
                self.show_doctor_appointments()

            elif choice == "3":
                self.logout()

            else:
                print(
                    "Invalid choice."
                )

    def nurse_menu(self):
        while (
            self.current_user
            and self.current_user["role"]
            == "nurse"
        ):

            print(
                "\n========== NURSE MENU =========="
            )
            print("1. Show Profile")
            print("2. Show My Doctors")
            print("3. Logout")

            choice = input(
                "Choose: "
            ).strip()

            if choice == "1":
                self.show_profile()

            elif choice == "2":
                self.show_my_doctors()

            elif choice == "3":
                self.logout()

            else:
                print(
                    "Invalid choice."
                )

    def main_menu(self):

        while True:

            print("\n")
            print(
                "===================================="
            )
            print(
                "         SMART CLINIC SYSTEM"
            )
            print(
                "===================================="
            )
            print("1. Login")
            print("2. Register Patient")
            print("3. Quit")

            choice = input(
                "Choose: "
            ).strip()

            if choice == "1":

                if self.login():

                    role = self.current_user[
                        "role"
                    ]

                    if role == "admin":
                        self.admin_menu()

                    elif role == "patient":
                        self.patient_menu()

                    elif role == "doctor":
                        self.doctor_menu()

                    elif role == "nurse":
                        self.nurse_menu()

            elif choice == "2":
                self.register_patient()

            elif choice == "3":
                self.save_data()
                print("Goodbye!")
                break

            else:
                print(
                    "Invalid choice."
                )


clinic = ClinicSystem()
clinic.main_menu()
