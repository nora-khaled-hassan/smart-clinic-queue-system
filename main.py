import json
import re
import hashlib
import secrets
from functools import reduce
from datetime import datetime, timedelta

class ClinicError(Exception):
    pass
class InvalidAppointmentTimeError(ClinicError):
    pass
class DoctorUnavailableError(ClinicError):
    pass
class DuplicateBookingError(ClinicError):
    pass
class MissingPatientError(ClinicError):
    pass
class MissingDoctorError(ClinicError):
    pass
class InvalidPaymentError(ClinicError):
    pass
class PatientNotInQueueError(ClinicError):
    pass
class InvalidCaseTypeError(ClinicError):
    pass
class VisitAlreadyCompletedError(ClinicError):
    pass
class PatientAlreadyCheckedInError(ClinicError):
    pass

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password

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
        super().__init__(
            user_id,
            name,
            phone
        )
        self.age = age
        self.case_type = case_type
        self.priority = priority
        self.appointments = (
            appointments
            if appointments is not None
            else []
        )

    def get_info(self):

        data = super().get_info()

        data.update({
            "patient_id": self.user_id,
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
        super().__init__(
            user_id,
            name,
            phone
        )

        self.specialty = specialty
        self.rate = rate
        self.appointment_duration = appointment_duration

        self.working_days = (
            working_days
            if working_days is not None
            else []
        )

        self.working_hours = (
            working_hours
            if working_hours is not None
            else {}
        )

        self.availability = availability

        self.assigned_nurses = (
            assigned_nurses
            if assigned_nurses is not None
            else []
        )

    def get_info(self):

        data = super().get_info()

        data.update({
            "doctor_id": self.user_id,
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
        super().__init__(
            user_id,
            name,
            phone
        )

        self.assigned_doctors = (
            assigned_doctors
            if assigned_doctors is not None
            else []
        )

        self.availability = availability

    def get_info(self):
        data = super().get_info()
        data.update({
            "nurse_id": self.user_id,
            "assigned_doctors": self.assigned_doctors,
            "availability": self.availability
        })
        return data

class UserAccount:
    def __init__(
        self,
        user_id,
        name,
        phone,
        role,
        password
    ):
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

class Appointment:
    def __init__(
        self,
        appointment_id,
        patient_id,
        doctor_id,
        date,
        time,
        service_type="consultation",
        status="BOOKED",
        payment_status="UNPAID",
        case_type=None,
        priority=None,
        arrival_time=None
    ):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.time = time
        self.service_type = service_type
        self.status = status
        self.payment_status = payment_status
        self.case_type = case_type
        self.priority = priority
        self.arrival_time = arrival_time

    def update_status(self, new_status):
        valid_statuses = [
            "BOOKED",
            "CONFIRMED",
            "CHECKED_IN",
            "WAITING",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
            "NO_SHOW"
        ]
        new_status = new_status.upper()
        if new_status not in valid_statuses:
            raise InvalidAppointmentTimeError(
                "Invalid appointment status."
            )
        self.status = new_status

    def get_info(self):
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "date": self.date,
            "time": self.time,
            "service_type": self.service_type,
            "status": self.status,
            "payment_status": self.payment_status,
            "case_type": self.case_type,
            "priority": self.priority,
            "arrival_time": self.arrival_time
        }

class Payment:
    def __init__(
        self,
        payment_code,
        confirmation_number,
        amount,
        status="PENDING",
        appointment_id=None,
        patient_id=None
    ):
        self.payment_code = payment_code
        self.confirmation_number = confirmation_number
        self.amount = amount
        self.status = status
        self.appointment_id = appointment_id
        self.patient_id = patient_id
    def process_payment(self):

        if self.amount <= 0:
            raise InvalidPaymentError(
                "Invalid payment amount."
            )
        if self.status == "PAID":
            raise InvalidPaymentError(
                "Payment has already been completed."
            )
        self.status = "PAID"
        if not self.confirmation_number:
            self.confirmation_number = (
                secrets.randbelow(900000000) + 100000000
            )
        return True

    def get_info(self):
        return {
            "payment_code": self.payment_code,
            "confirmation_number": self.confirmation_number,
            "amount": self.amount,
            "status": self.status,
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id
        }

class Bill:
    def __init__(
        self,
        bill_id,
        patient_id,
        doctor_id,
        service_type,
        base_rate,
        doctor_rate,
        total,
        payment_status="UNPAID"
    ):
        self.bill_id = bill_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.service_type = service_type
        self.base_rate = base_rate
        self.doctor_rate = doctor_rate
        self.total = total
        self.payment_status = payment_status

    def get_info(self):
        return {
            "bill_id": self.bill_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "service_type": self.service_type,
            "base_rate": self.base_rate,
            "doctor_rate": self.doctor_rate,
            "total": self.total,
            "payment_status": self.payment_status
        }

class Visit:
    def __init__(
        self,
        visit_id,
        patient_id,
        doctor_id,
        case_type=None,
        priority=None,
        diagnosis=None,
        treatment=None,
        follow_up=None,
        status="WAITING"
    ):
        self.visit_id = visit_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.case_type = case_type
        self.priority = priority
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.follow_up = follow_up
        self.status = status

    def complete_visit(self):
        if self.status == "COMPLETED":
            raise VisitAlreadyCompletedError(
                "Visit is already completed."
            )
        self.status = "COMPLETED"

    def get_info(self):
        return {
            "visit_id": self.visit_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "case_type": self.case_type,
            "priority": self.priority,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "follow_up": self.follow_up,
            "status": self.status
        }

class AppointmentIterator:
    def __init__(self, appointments):
        self.appointments = appointments
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.appointments):
            raise StopIteration
        appointment = self.appointments[
            self.index
        ]
        self.index += 1
        return appointment

class ClinicManager:
    def __init__(self):
        self.patients = []
        self.doctors = []
        self.nurses = []
        self.appointments = []
        self.visits = []
        self.bills = []
        self.payments = []
        self.users = []
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

class ClinicSystem(ClinicManager):
    def __init__(
        self,
        file_name="clinic_data.json"
    ):
        super().__init__()
        self.file_name = file_name
        self.current_user = None
        self.load_data()
        self.create_default_admin()

    def load_data(self):
        try:
            with open(
                self.file_name,
                "r"
            ) as file:

                data = json.load(file)
            self.users = data.get(
                "users",
                []
            )
            self.patients = data.get(
                "patients",
                []
            )
            self.doctors = data.get(
                "doctors",
                []
            )
            self.nurses = data.get(
                "nurses",
                []
            )
            self.appointments = data.get(
                "appointments",
                []
            )
            self.visits = data.get(
                "visits",
                []
            )
            self.bills = data.get(
                "bills",
                []
            )
            self.payments = data.get(
                "payments",
                []
            )
            self.waiting_queue = data.get(
                "waiting_queue",
                []
            )
            self.action_history = data.get(
                "action_history",
                []
            )
            self.settings = data.get(
                "settings",
                self.settings
            )
            for doctor in self.doctors:
                if "appointment_duration" not in doctor:
                    doctor["appointment_duration"] = 30

            for user in self.users:
                if user.get("password_hashed") is None:
                    if user.get("password"):
                        user["password"] = hash_password(
                            user["password"]
                        )
                        user["password_hashed"] = True
            self.save_data()
        except FileNotFoundError:
            self.save_data()
        except json.JSONDecodeError:
            print(
                "Error: JSON file is not valid."
            )

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

        with open(
            self.file_name,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    def create_default_admin(self):
        for user in self.users:
            if user["user_id"] == "A001":
                return
        admin = {
            "user_id": "A001",
            "name": "Clinic Admin",
            "phone": "01000000000",
            "role": "admin",
            "password": hash_password(
                "admin123"
            ),
            "password_hashed": True
        }
        self.users.append(admin)
        self.save_data()

    def valid_id(
        self,
        user_id,
        role
    ):
        patterns = {
            "patient": r"^P\d{3}$",
            "doctor": r"^D\d{3}$",
            "nurse": r"^N\d{3}$",
            "admin": r"^A\d{3}$"
        }
        return re.fullmatch(
            patterns[role],
            user_id
        ) is not None

    def valid_phone(self, phone):
        return re.fullmatch(
            r"01[0125]\d{8}",
            phone
        ) is not None

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

    def find_appointment(
        self,
        appointment_id
    ):

        for appointment in self.appointments:
            if (
                appointment["appointment_id"]
                == appointment_id
            ):
                return appointment
        return None

    def find_visit(self, visit_id):
        for visit in self.visits:
            if visit["visit_id"] == visit_id:
                return visit
        return None

    def find_bill(self, bill_id):
        for bill in self.bills:
            if bill["bill_id"] == bill_id:
                return bill
        return None

    def find_payment_by_appointment(
        self,
        appointment_id
    ):

        for payment in self.payments:
            if (
                payment["appointment_id"]
                == appointment_id
            ):
                return payment
        return None

    def generate_patient_id(self):
        number = 1
        while True:
            patient_id = f"P{number:03d}"
            if not self.id_exists(
                patient_id
            ):
                return patient_id
            number += 1
    def generate_doctor_id(self):
        number = 1
        while True:
            doctor_id = f"D{number:03d}"
            if not self.id_exists(
                doctor_id
            ):
                return doctor_id
            number += 1

    def generate_nurse_id(self):
        number = 1
        while True:
            nurse_id = f"N{number:03d}"
            if not self.id_exists(
                nurse_id
            ):
                return nurse_id
            number += 1

    def generate_appointment_id(self):
        number = len(
            self.appointments
        ) + 1

        while True:
            appointment_id = (
                f"AP{number:03d}"
            )
            if not self.find_appointment(
                appointment_id
            ):
                return appointment_id
            number += 1

    def generate_visit_id(self):
        number = len(
            self.visits
        ) + 1
        while True:
            visit_id = f"V{number:03d}"
            if not self.find_visit(
                visit_id
            ):
                return visit_id
            number += 1

    def generate_bill_id(self):
        number = len(
            self.bills
        ) + 1
        while True:
            bill_id = f"B{number:03d}"
            if not self.find_bill(
                bill_id
            ):
                return bill_id
            number += 1

    def register_patient(self):
        print(
            "\n========== PATIENT REGISTRATION =========="
        )
        name = input(
            "Name: "
        ).strip()
        while not name:
            print(
                "Name cannot be empty."
            )
            name = input(
                "Name: "
            ).strip()
        while True:
            phone = input(
                "Phone: "
            ).strip()
            if self.valid_phone(phone):
                break
            print(
                "Invalid phone number."
            )
        while True:
            try:
                age = int(
                    input("Age: ")
                )
                if 0 < age <= 120:
                    break
                print(
                    "Invalid age."
                )
            except ValueError:
                print(
                    "Age must be a number."
                )
        password = input(
            "Password: "
        ).strip()
        while len(password) < 4:
            print(
                "Password must contain at least 4 characters."
            )
            password = input(
                "Password: "
            ).strip()
        patient_id = (
            self.generate_patient_id()
        )
        self.users.append({
            "user_id": patient_id,
            "name": name,
            "phone": phone,
            "role": "patient",
            "password": hash_password(password),
            "password_hashed": True
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
        self.action_history.append(
            f"Patient {patient_id} registered."
        )
        self.save_data()
        print(
            "\nPatient registered successfully."
        )
        print(
            f"Patient ID: {patient_id}"
        )

    def add_doctor(self):
        if (
            not self.current_user
            or self.current_user["role"]
            != "admin"
        ):
            print(
                "Access denied."
            )
            return
        print(
            "\n========== ADD DOCTOR =========="
        )

        name = input(
            "Doctor name: "
        ).strip()
        while not name:
            print(
                "Name cannot be empty."
            )
            name = input(
                "Doctor name: "
            ).strip()
        while True:
            phone = input(
                "Phone: "
            ).strip()
            if self.valid_phone(phone):
                break
            print(
                "Invalid phone number."
            )
        specialty = input(
            "Specialty: "
        ).strip()
        while not specialty:
            print(
                "Specialty cannot be empty."
            )
            specialty = input(
                "Specialty: "
            ).strip()
        while True:
            try:
                rate = float(
                    input(
                        "Doctor rate: "
                    )
                )
                if rate <= 0:
                    print(
                        "Rate must be greater than zero."
                    )
                    continue
                break
            except ValueError:
                print(
                    "Rate must be a number."
                )
        while True:
            try:
                duration = int(
                    input(
                        "Appointment duration in minutes: "
                    )
                )
                if duration <= 0:
                    print(
                        "Duration must be greater than zero."
                    )
                    continue
                break
            except ValueError:
                print(
                    "Duration must be a number."
                )
        days = [
            "Saturday",
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ]
        print(
            "\nAvailable working days:"
        )
        for i, day in enumerate(
            days,
            1
        ):
            print(
                f"{i}. {day}"
            )
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
                    print(
                        "Doctor must work exactly 3 days."
                    )
                    continue
                if len(set(numbers)) != 3:
                    print(
                        "You cannot choose the same day twice."
                    )
                    continue
                if any(
                    x < 1 or x > 7
                    for x in numbers
                ):
                    print(
                        "Invalid day."
                    )
                    continue
                working_days = [
                    days[x - 1]
                    for x in numbers
                ]
                break
            except ValueError:
                print(
                    "Invalid day input."
                )

        while True:
            start = input(
                "Starting time (HH:MM): "
            ).strip()
            if re.fullmatch(
                r"^(?:[01]\d|2[0-3]):[0-5]\d$",
                start
            ):
                break
            print(
                "Invalid starting time."
            )

        while True:
            end = input(
                "Ending time (HH:MM): "
            ).strip()
            if re.fullmatch(
                r"^(?:[01]\d|2[0-3]):[0-5]\d$",
                end
            ):
                break
            print(
                "Invalid ending time."
            )
        password = input(
            "Password: "
        ).strip()
        while len(password) < 4:
            print(
                "Password must contain at least 4 characters."
            )
            password = input(
                "Password: "
            ).strip()
        doctor_id = (
            self.generate_doctor_id()
        )
        self.users.append({
            "user_id": doctor_id,
            "name": name,
            "phone": phone,
            "role": "doctor",
            "password": hash_password(password),
            "password_hashed": True
        })
        self.doctors.append({
            "doctor_id": doctor_id,
            "name": name,
            "specialty": specialty,
            "phone": phone,
            "rate": rate,
            "appointment_duration": duration,
            "working_days": working_days,
            "working_hours": {
                "start": start,
                "end": end},
            "availability": True,
            "assigned_nurses": []
        })

        self.action_history.append(
            f"Doctor {doctor_id} added."
        )

        self.save_data()
        print(
            "\nDoctor added successfully."
        )
        print(
            f"Doctor ID: {doctor_id}"
        )

    def add_nurse(self):
        if (
            not self.current_user
            or self.current_user["role"]
            != "admin"
        ):
            print(
                "Access denied."
            )
            return
        print(
            "\n========== ADD NURSE =========="
        )
        name = input(
            "Nurse name: "
        ).strip()
        while not name:
            print(
                "Name cannot be empty."
            )
            name = input(
                "Nurse name: "
            ).strip()
        while True:
            phone = input(
                "Phone: "
            ).strip()
            if self.valid_phone(phone):
                break
            print(
                "Invalid phone number."
            )
        password = input(
            "Password: "
        ).strip()

        while len(password) < 4:
            print(
                "Password must contain at least 4 characters."
            )
            password = input(
                "Password: "
            ).strip()

        if not self.doctors:
            print(
                "No doctors available."
            )
            return
        print(
            "\n========== AVAILABLE DOCTORS =========="
        )
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
            doctor = self.find_doctor(
                doctor_id
            )
            if doctor:
                break
            print(
                "Doctor not found."
            )
        nurse_id = (
            self.generate_nurse_id()
        )
        nurse = {
            "nurse_id": nurse_id,
            "name": name,
            "phone": phone,
            "assigned_doctors": [
                doctor_id
            ],
            "availability": True
        }
        user = {
            "user_id": nurse_id,
            "name": name,
            "phone": phone,
            "role": "nurse",
            "password": hash_password(password),
            "password_hashed": True
        }
        self.users.append(user)
        self.nurses.append(nurse)
        doctor["assigned_nurses"].append(
            nurse_id
        )
        self.action_history.append(
            f"Nurse {nurse_id} added and assigned "
            f"to doctor {doctor_id}."
        )
        self.save_data()
        print(
            "\nNurse added successfully."
        )
        print(
            f"Nurse ID: {nurse_id}"
        )
        print(
            f"Assigned Doctor: {doctor_id}"
        )

    def login(self):
        print(
            "\n========== LOGIN =========="
        )
        user_id = input(
            "ID: "
        ).strip().upper()
        password = input(
            "Password: "
        ).strip()
        user = self.find_user(
            user_id
        )
        if user is None:
            print(
                "User not found."
            )
            return False
        if not verify_password(
            password,
            user["password"]
        ):
            print(
                "Wrong password."
            )
            return False
        self.current_user = user
        print(
            f"\nWelcome, {user['name']}!"
        )
        print(
            f"Role: {user['role'].upper()}"
        )
        return True

    def logout(self):
        if self.current_user:
            print(
                f"Goodbye, "
                f"{self.current_user['name']}."
            )
        self.current_user = None

    def show_profile(self):
        if not self.current_user:
            print(
                "Please login first."
            )
            return
        user_id = self.current_user[
            "user_id"
        ]
        role = self.current_user[
            "role"
        ]
        print(
            "\n========== PROFILE =========="
        )
        print(
            f"ID: {user_id}"
        )
        print(
            f"Name: "
            f"{self.current_user['name']}"
        )
        print(
            f"Phone: "
            f"{self.current_user['phone']}"
        )
        print(
            f"Role: {role}"
        )
        if role == "patient":
            patient = self.find_patient(
                user_id
            )
            if patient:
                print(
                    f"Age: {patient['age']}"
                )
                print(
                    f"Case Type: "
                    f"{patient['case_type']}"
                )
                print(
                    f"Priority: "
                    f"{patient['priority']}"
                )
                print(
                    f"Appointments: "
                    f"{len(patient['appointments'])}"
                )
        elif role == "doctor":
            doctor = self.find_doctor(
                user_id
            )
            if doctor:
                print(
                    f"Specialty: "
                    f"{doctor['specialty']}"
                )
                print(
                    f"Doctor Rate: "
                    f"{doctor['rate']}"
                )
                print(
                    f"Appointment Duration: "
                    f"{doctor.get('appointment_duration', 30)} "
                    f"minutes"
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
            nurse = self.find_nurse(
                user_id
            )
            if nurse:
                print(
                    f"Assigned Doctors: "
                    f"{', '.join(nurse['assigned_doctors'])}"
                )

    def show_patients(self):
        print(
            "\n========== PATIENTS =========="
        )
        if not self.patients:
            print(
                "No patients found."
            )
            return
        for patient in self.patients:
            print(
                f"{patient['patient_id']} | "
                f"{patient['name']} | "
                f"Age: {patient['age']} | "
                f"Phone: {patient['phone']} | "
                f"Case: {patient.get('case_type')}"
            )

    def show_doctors(self):
        print(
            "\n========== DOCTORS =========="
        )
        if not self.doctors:
            print(
                "No doctors found."
            )
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
            print(
                "No nurses found."
            )
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
                and doctor["specialty"]
                not in specialties
            ):
                specialties.append(
                    doctor["specialty"]
                )
        print(
            "\n========== SPECIALTIES =========="
        )
        for i, specialty in enumerate(
            specialties,
            1
        ):
            print(
                f"{i}. {specialty}"
            )
        return specialties

    def is_doctor_working(
        self,
        doctor,
        date
    ):
        try:
            day = datetime.strptime(
                date,
                "%Y-%m-%d"
            ).strftime("%A")

            return day in doctor[
                "working_days"
            ]
        except ValueError:
            return False

    def doctor_load(
        self,
        doctor_id,
        date
    ):
        count = 0
        for appointment in self.appointments:
            if (
                appointment["doctor_id"]
                == doctor_id
                and appointment["date"]
                == date
                and appointment["status"]
                != "CANCELLED"
            ):
                count += 1
        return count

    def recommend_doctors(
        self,
        specialty,
        date
    ):
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

    def get_available_slots(
        self,
        doctor,
        date
    ):
        if not doctor["availability"]:
            return []
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
        except (
            KeyError,
            ValueError
        ):
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
            + timedelta(
                minutes=duration
            )
            <= end
        ):
            time = current.strftime(
                "%H:%M"
            )
            if time not in booked_times:
                slots.append(time)
            current += timedelta(
                minutes=duration
            )
        return slots

    def check_duplicate_booking(
        self,
        patient_id,
        doctor_id,
        date,
        time
    ):
        for appointment in self.appointments:
            if (
                appointment["patient_id"]
                == patient_id
                and appointment["doctor_id"]
                == doctor_id
                and appointment["date"]
                == date
                and appointment["time"]
                == time
                and appointment["status"]
                != "CANCELLED"
            ):
                raise DuplicateBookingError(
                    "Duplicate booking detected."
                )

    def calculate_price(
        self,
        doctor,
        service_type
    ):
        service_type = service_type.lower()
        rates = self.settings[
            "service_rates"
        ]
        if service_type not in rates:
            raise InvalidPaymentError(
                "Invalid service type."
            )
        base_rate = rates[
            service_type
        ]
        doctor_rate = float(
            doctor["rate"]
        )
        total = (
            base_rate
            * doctor_rate
        )
        return (
            base_rate,
            doctor_rate,
            round(total, 3)
        )

    def generate_payment_code(self):
        while True:
            code = str(
                secrets.randbelow(
                    900000000000
                )
                + 100000000000
            )
            exists = any(
                payment["payment_code"]
                == code
                for payment in self.payments
            )
            if not exists:
                return code

    def generate_bill(
        self,
        appointment
    ):
        patient = self.find_patient(
            appointment["patient_id"]
        )
        if patient is None:
            raise MissingPatientError(
                "Patient not found."
            )
        doctor = self.find_doctor(
            appointment["doctor_id"]
        )
        if doctor is None:
            raise MissingDoctorError(
                "Doctor not found."
            )
        service_type = appointment.get(
            "service_type",
            "consultation"
        )
        base_rate, doctor_rate, total = (
            self.calculate_price(
                doctor,
                service_type
            )
        )
        bill_id = (
            self.generate_bill_id()
        )
        bill = Bill(
            bill_id,
            patient["patient_id"],
            doctor["doctor_id"],
            service_type,
            base_rate,
            doctor_rate,
            total
        )
        self.bills.append(
            bill.get_info()
        )
        return self.bills[-1]

    def create_payment(
        self,
        appointment
    ):
        bill = None
        for item in self.bills:
            if (
                item["patient_id"]
                == appointment["patient_id"]
                and item["doctor_id"]
                == appointment["doctor_id"]
                and item["payment_status"]
                == "UNPAID"
            ):
                bill = item
                break
        if bill is None:
            bill = self.generate_bill(
                appointment
            )
        payment_code = (
            self.generate_payment_code()
        )
        payment = Payment(
            payment_code,
            None,
            bill["total"],
            "PENDING",
            appointment["appointment_id"],
            appointment["patient_id"]
        )
        self.payments.append(
            payment.get_info()
        )
        appointment["payment_status"] = "PENDING"
        appointment["status"] = "CONFIRMED"
        return self.payments[-1]

    def book_appointment(self):
        if not self.current_user:
            print(
                "Please login first."
            )
            return
        if self.current_user["role"] != "patient":
            print(
                "Only patients can book appointments."
            )
            return
        patient_id = self.current_user[
            "user_id"
        ]
        patient = self.find_patient(
            patient_id
        )
        if patient is None:
            raise MissingPatientError(
                "Patient not found."
            )
        print("\n========== BOOK APPOINTMENT ==========")
        specialties = (self.show_specialties())
        if not specialties:
            print("No doctors available.")
            return

        while True:
            try:
                choice = int(
                    input(
                        "Choose specialty: "
                    )
                )
                if (
                    1
                    <= choice
                    <= len(specialties)
                ):
                    specialty = specialties[
                        choice - 1
                    ]
                    break
                print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")

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
                if (
                    selected_date.date()
                    < datetime.now().date()
                ):
                    print(
                        "You cannot book a past date."
                    )
                    continue
                break
            except ValueError:
                print("Invalid date.")
        doctors = (
            self.recommend_doctors(
                specialty,
                date))

        if not doctors:
            raise DoctorUnavailableError(
                "No available doctors.")
        print("\n========== AVAILABLE DOCTORS ==========")

        for i, item in enumerate(
            doctors,
            1
        ):

            doctor = item["doctor"]
            print(
                f"{i}. "
                f"{doctor['doctor_id']} | "
                f"{doctor['name']} | "
                f"{doctor['specialty']} | "
                f"Load: {item['load']}"
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
                print("Please enter a number.")

        slots = (
            self.get_available_slots(
                doctor,
                date))

        if not slots:
            raise DoctorUnavailableError(
                "No available time slots."
            )
        print(
            f"\n========== AVAILABLE TIMES "
            f"FOR {doctor['name']} =========="
        )
        for i, slot in enumerate(slots,1):
            print(f"{i}. {slot}")
        while True:
            try:
                time_choice = int(
                    input(
                        "Choose time: "))

                if (1 <= time_choice<= len(slots)):
                    time = slots[
                        time_choice - 1]
                    break

                print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")

        try:
            self.check_duplicate_booking(
                patient_id,
                doctor["doctor_id"],
                date,
                time
            )
        except DuplicateBookingError as error:
            print(f"Error: {error}")
            return
        print("\n========== SERVICE TYPE ==========")
        print("1. Consultation - 2.5")
        print("2. Examination - 3.75")
        print("3. Emergency - 6.75")

        while True:
            service_choice = input(
                "Choose service: "
            ).strip()
            service_map = {
                "1": "consultation",
                "2": "examination",
                "3": "emergency"
            }
            if service_choice in service_map:
                service_type = service_map[
                    service_choice
                ]
                break
            print("Invalid service.")
        appointment_id = (
            self.generate_appointment_id())

        appointment = Appointment(
            appointment_id,
            patient_id,
            doctor["doctor_id"],
            date,
            time,
            service_type,
            "BOOKED",
            "UNPAID",
            None,
            None,
            None
        )
        self.appointments.append(
            appointment.get_info()
        )
        patient["appointments"].append(appointment_id)

        bill = self.generate_bill(
            self.appointments[-1])

        payment = self.create_payment(
            self.appointments[-1])

        self.action_history.append(
            f"Patient {patient_id} booked "
            f"appointment {appointment_id}."
        )
        self.save_data()
        print("\n======================================")
        print("Appointment Confirmed")
        print("======================================")
        print(f"Appointment ID: {appointment_id}")
        print(f"Doctor: {doctor['name']}")
        print(f"Specialty: {doctor['specialty']}")
        print(f"Date: {date}")
        print(f"Time: {time}")
        print(f"Service: {service_type.upper()}")
        print(f"Doctor Rate: {doctor['rate']}")
        print(f"Base Rate: {bill['base_rate']}")
        print(f"Final Price: {bill['total']}")
        print("\n========== PAYMENT ==========")
        print(f"Payment Code: "
            f"{payment['payment_code']}")
        print("Payment Status: PENDING")
        print("\nUse the payment code to complete payment.")

    def process_payment(self):
        if not self.current_user:
            print("Please login first.")
            return
        patient_id = self.current_user["user_id"]
        pending_payments = [payment
            for payment in self.payments
            if (payment["patient_id"]== patient_id and payment["status"] == "PENDING")]
        if not pending_payments:
            print("No pending payments.")
            return
        print("\n========== PENDING PAYMENTS ==========")
        for payment in pending_payments:
            print(
                f"Appointment: "
                f"{payment['appointment_id']} | "
                f"Amount: {payment['amount']} | "
                f"Code: {payment['payment_code']}"
            )
        code = input(
            "\nEnter payment code: "
        ).strip()
        payment = None
        for item in pending_payments:
            if item["payment_code"] == code:
                payment = item
                break

        if payment is None:
            raise InvalidPaymentError("Invalid payment code.")
        payment_object = Payment(
            payment["payment_code"],
            payment["confirmation_number"],
            payment["amount"],
            payment["status"],
            payment["appointment_id"],
            payment["patient_id"])

        payment_object.process_payment()
        payment.update( payment_object.get_info())
        appointment = self.find_appointment(
            payment["appointment_id"])
        if appointment:
            appointment["payment_status"] = "PAID"
            appointment["status"] = "CONFIRMED"

        for bill in self.bills:
            if (
                bill["patient_id"]
                == patient_id
                and bill["doctor_id"]
                == appointment["doctor_id"]
                and bill["payment_status"]
                == "UNPAID"
            ):
                bill["payment_status"] = "PAID"
                break
        self.action_history.append(
            f"Patient {patient_id} paid "
            f"appointment {payment['appointment_id']}."
        )
        self.save_data()
        print("\nPayment Successful.")
        print(
            f"Confirmation Number: "
            f"{payment['confirmation_number']}")
        print(
            "Payment Status: PAID")

    def show_patient_appointments(self):
        if not self.current_user:
            return

        patient_id = self.current_user["user_id"]
        print("\n========== MY APPOINTMENTS ==========")
        found = False
        for appointment in self.appointments:
            if (
                appointment["patient_id"]
                == patient_id
            ):
                found = True
                doctor = self.find_doctor(
                    appointment["doctor_id"])
                doctor_name = (
                    doctor["name"]
                    if doctor
                    else appointment["doctor_id"])
                print(
                    f"{appointment['appointment_id']} | "
                    f"Doctor: {doctor_name} | "
                    f"Date: {appointment['date']} | "
                    f"Time: {appointment['time']} | "
                    f"Service: {appointment.get('service_type')} | "
                    f"Status: {appointment['status']} | "
                    f"Payment: {appointment['payment_status']}"
                )
        if not found:
            print("No appointments found.")

    def show_doctor_appointments(
        self,
        today_only=False
    ):
        if not self.current_user:
            return
        doctor_id = self.current_user["user_id"]
        appointments = []
        today = datetime.now().strftime("%Y-%m-%d")
        for appointment in self.appointments:
            if (
                appointment["doctor_id"]
                == doctor_id
            ):
                if today_only:
                    if appointment["date"] == today:
                        appointments.append(appointment)
                else:
                    appointments.append(appointment)

        appointments.sort(
            key=lambda x: (
                x["date"],
                x["time"]))

        print("\n========== DOCTOR APPOINTMENTS ==========")

        if not appointments:
            print("No appointments found.")
            return
        iterator = AppointmentIterator(appointments)
        for appointment in iterator:
            patient = self.find_patient(
                appointment["patient_id"])

            patient_name = (
                patient["name"]
                if patient
                else appointment["patient_id"]
            )
            print(
                f"{appointment['appointment_id']} | "
                f"Patient: {patient_name} | "
                f"Date: {appointment['date']} | "
                f"Time: {appointment['time']} | "
                f"Status: {appointment['status']} | "
                f"Payment: {appointment['payment_status']}"
            )

    def view_all_appointments(self):
        print("\n========== ALL APPOINTMENTS ==========")
        if not self.appointments:
            print("No appointments.")

            return

        appointments = sorted(
            self.appointments,
            key=lambda x: (
                x["date"],
                x["time"]
            )
        )

        iterator = AppointmentIterator(
            appointments
        )

        for appointment in iterator:

            print(
                f"{appointment['appointment_id']} | "
                f"P: {appointment['patient_id']} | "
                f"D: {appointment['doctor_id']} | "
                f"{appointment['date']} | "
                f"{appointment['time']} | "
                f"{appointment['status']} | "
                f"{appointment['payment_status']}"
            )

    def cancel_appointment(self):

        if not self.current_user:

            print(
                "Please login first."
            )

            return

        appointment_id = input(
            "Enter appointment ID: "
        ).strip().upper()

        appointment = self.find_appointment(
            appointment_id
        )

        if appointment is None:

            print(
                "Appointment not found."
            )

            return

        role = self.current_user[
            "role"
        ]

        user_id = self.current_user[
            "user_id"
        ]

        if (
            role == "patient"
            and appointment["patient_id"]
            != user_id
        ):

            print(
                "Access denied."
            )

            return

        if appointment["status"] == "CANCELLED":

            print(
                "Appointment is already cancelled."
            )

            return

        confirm = input(
            "Are you sure? (Y/N): "
        ).strip().upper()

        if confirm != "Y":

            print(
                "Cancellation cancelled."
            )

            return

        appointment[
            "status"
        ] = "CANCELLED"

        self.action_history.append(
            f"Appointment {appointment_id} cancelled."
        )

        self.save_data()

        print(
            "Appointment cancelled successfully."
        )

    def update_appointment_status(self):

        if not self.current_user:

            return

        appointment_id = input(
            "Appointment ID: "
        ).strip().upper()

        appointment = self.find_appointment(
            appointment_id
        )

        if appointment is None:

            print(
                "Appointment not found."
            )

            return

        print(
            "\n1. BOOKED"
        )

        print(
            "2. CONFIRMED"
        )

        print(
            "3. CHECKED_IN"
        )

        print(
            "4. WAITING"
        )

        print(
            "5. IN_PROGRESS"
        )

        print(
            "6. COMPLETED"
        )

        print(
            "7. CANCELLED"
        )

        status_map = {

            "1": "BOOKED",

            "2": "CONFIRMED",

            "3": "CHECKED_IN",

            "4": "WAITING",

            "5": "IN_PROGRESS",

            "6": "COMPLETED",

            "7": "CANCELLED"
        }

        choice = input(
            "Choose status: "
        ).strip()

        if choice not in status_map:

            print(
                "Invalid status."
            )

            return

        appointment[
            "status"
        ] = status_map[choice]

        self.action_history.append(
            f"Appointment {appointment_id} "
            f"updated to "
            f"{status_map[choice]}."
        )

        self.save_data()

        print(
            "Appointment status updated."
        )

    def check_in_patient(self):

        if not self.current_user:

            print(
                "Please login first."
            )

            return

        if self.current_user["role"] != "nurse":

            print(
                "Only nurses can check in patients."
            )

            return

        confirmation = input(
            "Enter payment confirmation number: "
        ).strip()

        payment = None

        for item in self.payments:

            if (
                str(
                    item["confirmation_number"]
                )
                == confirmation
                and item["status"]
                == "PAID"
            ):

                payment = item

                break

        if payment is None:

            raise InvalidPaymentError(
                "Payment confirmation is invalid."
            )

        appointment = self.find_appointment(
            payment["appointment_id"]
        )

        if appointment is None:

            raise MissingPatientError(
                "Appointment not found."
            )

        if appointment[
            "payment_status"
        ] != "PAID":

            raise InvalidPaymentError(
                "Appointment is not paid."
            )

        if appointment[
            "status"
        ] in [
            "CHECKED_IN",
            "WAITING"
        ]:

            raise PatientAlreadyCheckedInError(
                "Patient already checked in."
            )

        nurse = self.find_nurse(
            self.current_user["user_id"]
        )

        if (
            appointment["doctor_id"]
            not in nurse["assigned_doctors"]
        ):

            print(
                "This patient is not assigned "
                "to your doctors."
            )

            return

        arrival_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        appointment[
            "arrival_time"
        ] = arrival_time

        appointment[
            "status"
        ] = "WAITING"

        patient = self.find_patient(
            appointment["patient_id"]
        )

        if patient is None:

            raise MissingPatientError(
                "Patient not found."
            )

        case_type = patient.get(
            "case_type"
        )

        if case_type:

            priority = self.get_priority(
                case_type
            )

            appointment[
                "case_type"
            ] = case_type

            appointment[
                "priority"
            ] = priority

        else:

            appointment[
                "case_type"
            ] = "regular"

            appointment[
                "priority"
            ] = 3

        if appointment["appointment_id"] not in [
            item["appointment_id"]
            for item in self.waiting_queue
        ]:

            self.waiting_queue.append({

                "appointment_id":
                    appointment["appointment_id"],

                "patient_id":
                    appointment["patient_id"],

                "doctor_id":
                    appointment["doctor_id"],

                "priority":
                    appointment["priority"],

                "arrival_time":
                    arrival_time
            })

        self.sort_waiting_queue()

        self.action_history.append(
            f"Nurse {self.current_user['user_id']} "
            f"checked in patient "
            f"{appointment['patient_id']}."
        )

        self.save_data()

        print(
            "\nPatient checked in successfully."
        )

        print(
            "Status: WAITING"
        )

    def create_triage_rule(self):

        evaluated_cases = 0

        def triage_rule(case_type):

            nonlocal evaluated_cases

            case_type = case_type.lower()

            rules = {

                "emergency": 1,

                "urgent": 2,

                "regular": 3
            }

            if case_type not in rules:

                raise InvalidCaseTypeError(
                    "Invalid case type."
                )

            evaluated_cases += 1

            return rules[case_type]

        return triage_rule

    def get_priority(
        self,
        case_type
    ):

        triage_rule = (
            self.create_triage_rule()
        )

        return triage_rule(
            case_type
        )

    def sort_waiting_queue(self):

        self.waiting_queue.sort(
            key=lambda x: (
                x["priority"],
                x["arrival_time"]
            )
        )


    def show_waiting_queue(self):

        self.sort_waiting_queue()

        print(
            "\n========== WAITING QUEUE =========="
        )

        if not self.waiting_queue:

            print(
                "Waiting queue is empty."
            )

            return

        for index, item in enumerate(
            self.waiting_queue,
            1
        ):

            patient = self.find_patient(
                item["patient_id"]
            )

            name = (
                patient["name"]
                if patient
                else item["patient_id"]
            )

            priority_name = {

                1: "EMERGENCY",

                2: "URGENT",

                3: "REGULAR"
            }.get(
                item["priority"],
                "UNKNOWN"
            )

            print(
                f"{index}. "
                f"{item['patient_id']} | "
                f"{name} | "
                f"{priority_name} | "
                f"Arrival: {item['arrival_time']} | "
                f"Doctor: {item['doctor_id']}"
            )

    def show_emergency_cases(self):

        emergency_cases = list(
            filter(
                lambda item:
                    item["priority"] == 1,
                self.waiting_queue
            )
        )

        print(
            "\n========== EMERGENCY CASES =========="
        )

        if not emergency_cases:

            print(
                "No emergency cases."
            )

            return

        for item in emergency_cases:

            patient = self.find_patient(
                item["patient_id"]
            )

            name = (
                patient["name"]
                if patient
                else item["patient_id"]
            )

            print(
                f"{item['patient_id']} | "
                f"{name} | "
                f"Arrival: {item['arrival_time']} | "
                f"Doctor: {item['doctor_id']}"
            )

    def search_patient(self):

        keyword = input(
            "Enter patient ID or name: "
        ).strip().lower()

        found = False

        print(
            "\n========== SEARCH RESULTS =========="
        )

        for patient in self.patients:

            if (
                keyword
                in patient["patient_id"].lower()
                or keyword
                in patient["name"].lower()
            ):

                found = True

                print(
                    f"ID: {patient['patient_id']}"
                )

                print(
                    f"Name: {patient['name']}"
                )

                print(
                    f"Age: {patient['age']}"
                )

                print(
                    f"Phone: {patient['phone']}"
                )

                print(
                    f"Case Type: "
                    f"{patient['case_type']}"
                )

                print(
                    f"Priority: "
                    f"{patient['priority']}"
                )

                print(
                    "--------------------------------"
                )

        if not found:

            print(
                "Patient not found."
            )


    def set_case_type(
        self,
        patient_id=None
    ):

        if patient_id is None:

            patient_id = input(
                "Patient ID: "
            ).strip().upper()

        patient = self.find_patient(
            patient_id
        )

        if patient is None:

            raise MissingPatientError(
                "Patient not found."
            )

        print(
            "\n1. Regular"
        )

        print(
            "2. Urgent"
        )

        print(
            "3. Emergency"
        )

        case_map = {

            "1": "regular",

            "2": "urgent",

            "3": "emergency"
        }

        choice = input(
            "Choose case type: "
        ).strip()

        if choice not in case_map:

            raise InvalidCaseTypeError(
                "Invalid case type."
            )

        case_type = case_map[
            choice
        ]

        priority = self.get_priority(
            case_type
        )

        patient[
            "case_type"
        ] = case_type

        patient[
            "priority"
        ] = priority

        print(
            f"Case Type: "
            f"{case_type.upper()}"
        )

        print(
            f"Priority: P{priority}"
        )

        self.save_data()


    def start_visit(self):

        if not self.current_user:

            return

        doctor_id = self.current_user[
            "user_id"
        ]

        self.show_doctor_waiting_queue()

        appointment_id = input(
            "\nEnter appointment ID: "
        ).strip().upper()

        appointment = self.find_appointment(
            appointment_id
        )

        if appointment is None:

            print(
                "Appointment not found."
            )

            return

        if appointment["doctor_id"] != doctor_id:

            print(
                "This appointment does not "
                "belong to you."
            )

            return

        if appointment["status"] != "WAITING":

            print(
                "Patient is not waiting."
            )

            return

        appointment[
            "status"
        ] = "IN_PROGRESS"

        patient = self.find_patient(
            appointment["patient_id"]
        )

        if patient is None:

            raise MissingPatientError(
                "Patient not found."
            )

        visit_id = (
            self.generate_visit_id()
        )

        visit = Visit(

            visit_id,

            patient["patient_id"],

            doctor_id,

            patient.get("case_type"),

            patient.get("priority"),

            None,

            None,

            None,

            "IN_PROGRESS"
        )

        self.visits.append(
            visit.get_info()
        )

        self.waiting_queue = [

            item

            for item in self.waiting_queue

            if item["appointment_id"]
            != appointment_id
        ]

        self.action_history.append(
            f"Doctor {doctor_id} started visit "
            f"{visit_id}."
        )

        self.save_data()

        print(
            "\nVisit started successfully."
        )

        print(
            f"Visit ID: {visit_id}"
        )

    def show_doctor_waiting_queue(self):

        if not self.current_user:

            return

        doctor_id = self.current_user[
            "user_id"
        ]

        queue = [

            item

            for item in self.waiting_queue

            if item["doctor_id"] == doctor_id
        ]

        queue.sort(
            key=lambda x: (
                x["priority"],
                x["arrival_time"]
            )
        )

        print(
            "\n========== MY WAITING QUEUE =========="
        )

        if not queue:

            print(
                "No patients waiting."
            )

            return

        for item in queue:

            patient = self.find_patient(
                item["patient_id"]
            )

            name = (
                patient["name"]
                if patient
                else item["patient_id"]
            )

            print(
                f"{item['appointment_id']} | "
                f"{item['patient_id']} | "
                f"{name} | "
                f"P{item['priority']} | "
                f"{item['arrival_time']}"
            )

    def assess_patient(self):

        if not self.current_user:

            return

        doctor_id = self.current_user[
            "user_id"
        ]

        visit_id = input(
            "Visit ID: "
        ).strip().upper()

        visit = self.find_visit(
            visit_id
        )

        if visit is None:

            print(
                "Visit not found."
            )

            return

        if visit["doctor_id"] != doctor_id:

            print(
                "Access denied."
            )

            return

        if visit["status"] == "COMPLETED":

            raise VisitAlreadyCompletedError(
                "Visit already completed."
            )

        print(
            "\n========== PATIENT ASSESSMENT =========="
        )

        self.set_case_type(
            visit["patient_id"]
        )

        patient = self.find_patient(
            visit["patient_id"]
        )

        visit[
            "case_type"
        ] = patient["case_type"]

        visit[
            "priority"
        ] = patient["priority"]

        diagnosis = input(
            "Diagnosis: "
        ).strip()

        treatment = input(
            "Treatment: "
        ).strip()

        follow_up = input(
            "Follow-up: "
        ).strip()

        visit[
            "diagnosis"
        ] = diagnosis

        visit[
            "treatment"
        ] = treatment

        visit[
            "follow_up"
        ] = follow_up

        self.save_data()

        print(
            "Assessment saved successfully."
        )


    def complete_visit(self):

        if not self.current_user:

            return

        visit_id = input(
            "Visit ID: "
        ).strip().upper()

        visit = self.find_visit(
            visit_id
        )

        if visit is None:

            print(
                "Visit not found."
            )

            return

        if visit["doctor_id"] != self.current_user[
            "user_id"
        ]:

            print(
                "Access denied."
            )

            return

        visit_object = Visit(

            visit["visit_id"],

            visit["patient_id"],

            visit["doctor_id"],

            visit["case_type"],

            visit["priority"],

            visit["diagnosis"],

            visit["treatment"],

            visit["follow_up"],

            visit["status"]
        )

        visit_object.complete_visit()

        visit.update(
            visit_object.get_info()
        )

        appointment = None

        for item in self.appointments:

            if (
                item["patient_id"]
                == visit["patient_id"]
                and item["doctor_id"]
                == visit["doctor_id"]
                and item["status"]
                == "IN_PROGRESS"
            ):

                appointment = item

                break

        if appointment:

            appointment[
                "status"
            ] = "COMPLETED"

        self.action_history.append(
            f"Doctor {self.current_user['user_id']} "
            f"completed visit {visit_id}."
        )

        self.save_data()

        print(
            "\nVisit completed successfully."
        )

    def patient_history(self):

        if not self.current_user:

            return

        if self.current_user["role"] == "patient":

            patient_id = self.current_user[
                "user_id"
            ]

        else:

            patient_id = input(
                "Patient ID: "
            ).strip().upper()

        visits = [

            visit

            for visit in self.visits

            if visit["patient_id"]
            == patient_id
        ]

        print(
            "\n========== PATIENT HISTORY =========="
        )

        if not visits:

            print(
                "No visit history."
            )

            return

        for visit in visits:

            print(
                f"Visit: {visit['visit_id']}"
            )

            print(
                f"Doctor: {visit['doctor_id']}"
            )

            print(
                f"Case: {visit['case_type']}"
            )

            print(
                f"Priority: "
                f"P{visit['priority']}"
            )

            print(
                f"Diagnosis: "
                f"{visit['diagnosis']}"
            )

            print(
                f"Treatment: "
                f"{visit['treatment']}"
            )

            print(
                f"Follow-up: "
                f"{visit['follow_up']}"
            )

            print(
                f"Status: {visit['status']}"
            )

            print(
                "--------------------------------"
            )

    def doctor_schedule(self):

        if not self.current_user:

            return

        doctor_id = self.current_user[
            "user_id"
        ]

        doctor = self.find_doctor(
            doctor_id
        )

        if doctor is None:

            return

        print(
            "\n========== DOCTOR SCHEDULE =========="
        )

        print(
            f"Doctor: {doctor['name']}"
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

        print(
            f"Appointment Duration: "
            f"{doctor.get('appointment_duration', 30)} minutes"
        )


    def show_my_doctors(self):

        nurse = self.find_nurse(
            self.current_user["user_id"]
        )

        if not nurse:

            print(
                "Nurse not found."
            )

            return

        print(
            "\n========== MY DOCTORS =========="
        )

        for doctor_id in nurse[
            "assigned_doctors"
        ]:

            doctor = self.find_doctor(
                doctor_id
            )

            if not doctor:

                continue

            print(
                f"\n{doctor['doctor_id']} | "
                f"{doctor['name']} | "
                f"{doctor['specialty']}"
            )

    def generate_report(
        self,
        report_date=None
    ):

        if report_date is None:

            report_date = datetime.now().strftime(
                "%Y-%m-%d"
            )

        daily_appointments = [

            appointment

            for appointment in self.appointments

            if appointment["date"]
            == report_date
        ]

        completed_visits = [

            visit

            for visit in self.visits

            if visit["status"]
            == "COMPLETED"
        ]

        waiting = [

            appointment

            for appointment in daily_appointments

            if appointment["status"]
            in [
                "WAITING",
                "CHECKED_IN"
            ]
        ]

        cancelled = [

            appointment

            for appointment in daily_appointments

            if appointment["status"]
            == "CANCELLED"
        ]

        emergency = [

            appointment

            for appointment in daily_appointments

            if appointment.get("case_type")
            == "emergency"
        ]

        urgent = [

            appointment

            for appointment in daily_appointments

            if appointment.get("case_type")
            == "urgent"
        ]

        regular = [

            appointment

            for appointment in daily_appointments

            if appointment.get("case_type")
            in [
                "regular",
                None
            ]
        ]

        paid_appointments = [

            appointment

            for appointment in daily_appointments

            if appointment["payment_status"]
            == "PAID"
        ]

        unpaid_appointments = [

            appointment

            for appointment in daily_appointments

            if appointment["payment_status"]
            != "PAID"
        ]

        working_doctors = [

            doctor

            for doctor in self.doctors

            if doctor["availability"]
            and self.is_doctor_working(
                doctor,
                report_date
            )
        ]

        working_nurses = [

            nurse

            for nurse in self.nurses

            if nurse["availability"]
        ]

        # ----------------------------------------------------
        # MAP + REDUCE
        # ----------------------------------------------------

        paid_bills = [

            bill

            for bill in self.bills

            if bill["payment_status"]
            == "PAID"
        ]

        bill_amounts = list(
            map(
                lambda bill:
                    bill["total"],
                paid_bills
            )
        )

        total_revenue = reduce(
            lambda x, y: x + y,
            bill_amounts,
            0
        )

        report = {

            "date": report_date,

            "total_patients":
                len(self.patients),

            "completed_visits":
                len(completed_visits),

            "waiting_patients":
                len(waiting),

            "cancelled":
                len(cancelled),

            "emergency_cases":
                len(emergency),

            "urgent_cases":
                len(urgent),

            "regular_cases":
                len(regular),

            "doctors_working":
                len(working_doctors),

            "nurses_working":
                len(working_nurses),

            "paid_appointments":
                len(paid_appointments),

            "unpaid_appointments":
                len(unpaid_appointments),

            "total_revenue":
                round(total_revenue, 3)
        }

        return report

    def show_daily_report(self):

        report = self.generate_report()

        print(
            "\n========================================"
        )

        print(
            "             DAILY REPORT"
        )
        print(
            "========================================"
        )
        print(
            f"Date: {report['date']}"
        )
        print(
            f"Total Patients: "
            f"{report['total_patients']}"
        )

        print(
            f"Completed Visits: "
            f"{report['completed_visits']}"
        )

        print(
            f"Waiting Patients: "
            f"{report['waiting_patients']}"
        )

        print(
            f"Cancelled: "
            f"{report['cancelled']}"
        )

        print(
            f"Emergency Cases: "
            f"{report['emergency_cases']}"
        )

        print(
            f"Urgent Cases: "
            f"{report['urgent_cases']}"
        )

        print(
            f"Regular Cases: "
            f"{report['regular_cases']}"
        )

        print(
            f"Doctors Working: "
            f"{report['doctors_working']}"
        )

        print(
            f"Nurses Working: "
            f"{report['nurses_working']}"
        )

        print(
            f"Paid Appointments: "
            f"{report['paid_appointments']}"
        )

        print(
            f"Unpaid Appointments: "
            f"{report['unpaid_appointments']}"
        )

        print(
            f"Total Revenue: "
            f"{report['total_revenue']}"
        )

    def doctor_revenue_report(self):

        print(
            "\n========== DOCTOR REVENUE =========="
        )

        for doctor in self.doctors:

            doctor_id = doctor[
                "doctor_id"
            ]

            doctor_bills = [

                bill

                for bill in self.bills

                if (
                    bill["doctor_id"]
                    == doctor_id
                    and bill["payment_status"]
                    == "PAID"
                )
            ]

            amounts = list(
                map(
                    lambda bill:
                        bill["total"],
                    doctor_bills
                )
            )

            revenue = reduce(
                lambda x, y: x + y,
                amounts,
                0
            )

            print(
                f"{doctor_id} | "
                f"{doctor['name']} | "
                f"Revenue: "
                f"{round(revenue, 3)}"
            )


    def show_action_history(self):

        print(
            "\n========== ACTION HISTORY =========="
        )

        if not self.action_history:

            print(
                "No actions recorded."
            )

            return

        for index, action in enumerate(
            self.action_history,
            1
        ):

            print(
                f"{index}. {action}"
            )

    def remove_patient(self):

        patient_id = input(
            "Patient ID: "
        ).strip().upper()

        patient = self.find_patient(
            patient_id
        )

        if patient is None:

            print(
                "Patient not found."
            )

            return

        confirm = input(
            "Are you sure? (Y/N): "
        ).strip().upper()

        if confirm != "Y":

            print(
                "Operation cancelled."
            )

            return

        self.patients = [

            p

            for p in self.patients

            if p["patient_id"]
            != patient_id
        ]

        self.users = [

            user

            for user in self.users

            if user["user_id"]
            != patient_id
        ]

        self.action_history.append(
            f"Patient {patient_id} removed."
        )

        self.save_data()

        print(
            "Patient removed successfully."
        )

    def remove_doctor(self):

        doctor_id = input(
            "Doctor ID: "
        ).strip().upper()

        doctor = self.find_doctor(
            doctor_id
        )

        if doctor is None:

            print(
                "Doctor not found."
            )

            return

        confirm = input(
            "Are you sure? (Y/N): "
        ).strip().upper()

        if confirm != "Y":

            print(
                "Operation cancelled."
            )

            return

        self.doctors = [

            d

            for d in self.doctors

            if d["doctor_id"]
            != doctor_id
        ]

        self.users = [

            user

            for user in self.users

            if user["user_id"]
            != doctor_id
        ]

        self.action_history.append(
            f"Doctor {doctor_id} removed."
        )

        self.save_data()

        print(
            "Doctor removed successfully."
        )

    def remove_nurse(self):

        nurse_id = input(
            "Nurse ID: "
        ).strip().upper()

        nurse = self.find_nurse(
            nurse_id
        )

        if nurse is None:

            print(
                "Nurse not found."
            )

            return

        confirm = input(
            "Are you sure? (Y/N): "
        ).strip().upper()

        if confirm != "Y":

            print(
                "Operation cancelled."
            )

            return

        self.nurses = [

            n

            for n in self.nurses

            if n["nurse_id"]
            != nurse_id
        ]

        self.users = [

            user

            for user in self.users

            if user["user_id"]
            != nurse_id
        ]

        for doctor in self.doctors:

            if nurse_id in doctor[
                "assigned_nurses"
            ]:

                doctor[
                    "assigned_nurses"
                ].remove(
                    nurse_id
                )

        self.action_history.append(
            f"Nurse {nurse_id} removed."
        )

        self.save_data()

        print(
            "Nurse removed successfully."
        )

    def admin_menu(self):

        while (
            self.current_user
            and self.current_user["role"]
            == "admin"
        ):

            print(
                "\n===================================="
            )

            print(
                "             ADMIN MENU"
            )

            print(
                "===================================="
            )

            print(
                "1. Add Doctor"
            )

            print(
                "2. Add Nurse"
            )

            print(
                "3. Show Patients"
            )

            print(
                "4. Show Doctors"
            )

            print(
                "5. Show Nurses"
            )

            print(
                "6. View All Appointments"
            )

            print(
                "7. Daily Report"
            )

            print(
                "8. Doctor Revenue Report"
            )

            print(
                "9. Action History"
            )

            print(
                "10. Remove Patient"
            )

            print(
                "11. Remove Doctor"
            )

            print(
                "12. Remove Nurse"
            )

            print(
                "13. Show Profile"
            )

            print(
                "14. Logout"
            )

            choice = input(
                "Choose: "
            ).strip()

            try:

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

                    self.view_all_appointments()

                elif choice == "7":

                    self.show_daily_report()

                elif choice == "8":

                    self.doctor_revenue_report()

                elif choice == "9":

                    self.show_action_history()

                elif choice == "10":

                    self.remove_patient()

                elif choice == "11":

                    self.remove_doctor()

                elif choice == "12":

                    self.remove_nurse()

                elif choice == "13":

                    self.show_profile()

                elif choice == "14":

                    self.logout()

                else:

                    print(
                        "Invalid choice."
                    )

            except ClinicError as error:

                print(
                    f"\nError: {error}"
                )

    def patient_menu(self):

        while (
            self.current_user
            and self.current_user["role"]
            == "patient"
        ):

            print(
                "\n===================================="
            )

            print(
                "            PATIENT MENU"
            )

            print(
                "===================================="
            )

            print(
                "1. Book Appointment"
            )

            print(
                "2. View Appointments"
            )

            print(
                "3. Make Payment"
            )

            print(
                "4. Cancel Appointment"
            )

            print(
                "5. Patient History"
            )

            print(
                "6. Show Profile"
            )

            print(
                "7. Logout"
            )

            choice = input(
                "Choose: "
            ).strip()

            try:

                if choice == "1":

                    self.book_appointment()

                elif choice == "2":

                    self.show_patient_appointments()

                elif choice == "3":

                    self.process_payment()

                elif choice == "4":

                    self.cancel_appointment()

                elif choice == "5":

                    self.patient_history()

                elif choice == "6":

                    self.show_profile()

                elif choice == "7":

                    self.logout()

                else:

                    print(
                        "Invalid choice."
                    )

            except ClinicError as error:

                print(
                    f"\nError: {error}"
                )


    def nurse_menu(self):

        while (
            self.current_user
            and self.current_user["role"]
            == "nurse"
        ):

            print(
                "\n===================================="
            )

            print(
                "             NURSE MENU"
            )

            print(
                "===================================="
            )

            print(
                "1. Today's Appointments"
            )

            print(
                "2. Doctor Schedule"
            )

            print(
                "3. Check-In Patient"
            )

            print(
                "4. Waiting Queue"
            )

            print(
                "5. Emergency Cases"
            )

            print(
                "6. Search Patient"
            )

            print(
                "7. Update Appointment Status"
            )

            print(
                "8. My Doctors"
            )

            print(
                "9. Show Profile"
            )

            print(
                "10. Logout"
            )

            choice = input(
                "Choose: "
            ).strip()

            try:

                nurse = self.find_nurse(
                    self.current_user["user_id"]
                )

                if choice == "1":

                    print(
                        "\n========== TODAY'S APPOINTMENTS =========="
                    )

                    today = datetime.now().strftime(
                        "%Y-%m-%d"
                    )

                    for doctor_id in nurse[
                        "assigned_doctors"
                    ]:

                        for appointment in self.appointments:

                            if (
                                appointment["doctor_id"]
                                == doctor_id
                                and appointment["date"]
                                == today
                            ):

                                print(
                                    f"{appointment['appointment_id']} | "
                                    f"Patient: "
                                    f"{appointment['patient_id']} | "
                                    f"{appointment['time']} | "
                                    f"{appointment['status']}"
                                )

                elif choice == "2":

                    self.show_my_doctors()

                elif choice == "3":

                    self.check_in_patient()

                elif choice == "4":

                    self.show_waiting_queue()

                elif choice == "5":

                    self.show_emergency_cases()

                elif choice == "6":

                    self.search_patient()

                elif choice == "7":

                    self.update_appointment_status()

                elif choice == "8":

                    self.show_my_doctors()

                elif choice == "9":

                    self.show_profile()

                elif choice == "10":

                    self.logout()

                else:

                    print(
                        "Invalid choice."
                    )

            except ClinicError as error:

                print(
                    f"\nError: {error}"
                )

    def doctor_menu(self):

        while (
            self.current_user
            and self.current_user["role"]
            == "doctor"
        ):

            print(
                "\n===================================="
            )

            print(
                "             DOCTOR MENU"
            )

            print(
                "===================================="
            )

            print(
                "1. Today's Appointments"
            )

            print(
                "2. Doctor Schedule"
            )

            print(
                "3. Waiting Queue"
            )

            print(
                "4. Patient History"
            )

            print(
                "5. Start Visit"
            )

            print(
                "6. Assess Patient"
            )

            print(
                "7. Set Case Type"
            )

            print(
                "8. Diagnosis / Treatment / Follow-up"
            )

            print(
                "9. Complete Visit"
            )

            print(
                "10. Update Appointment Status"
            )

            print(
                "11. Show Profile"
            )

            print(
                "12. Logout"
            )

            choice = input(
                "Choose: "
            ).strip()

            try:

                if choice == "1":

                    self.show_doctor_appointments(
                        today_only=True
                    )

                elif choice == "2":

                    self.doctor_schedule()

                elif choice == "3":

                    self.show_doctor_waiting_queue()

                elif choice == "4":

                    self.patient_history()

                elif choice == "5":

                    self.start_visit()

                elif choice == "6":

                    self.assess_patient()

                elif choice == "7":

                    patient_id = input(
                        "Patient ID: "
                    ).strip().upper()

                    self.set_case_type(
                        patient_id
                    )

                elif choice == "8":

                    self.assess_patient()

                elif choice == "9":

                    self.complete_visit()

                elif choice == "10":

                    self.update_appointment_status()

                elif choice == "11":

                    self.show_profile()

                elif choice == "12":

                    self.logout()

                else:

                    print(
                        "Invalid choice."
                    )

            except ClinicError as error:

                print(
                    f"\nError: {error}"
                )

    def main_menu(self):

        while True:

            print(
                "\n"
            )

            print(
                "=========================================="
            )

            print(
                "          SMART CLINIC SYSTEM"
            )

            print(
                "=========================================="
            )

            print(
                "1. Login"
            )
            print(
                "2. Register Patient"
            )
            print(
                "3. Quit"
            )
            choice = input(
                "Choose: "
            ).strip()
            try:
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

                    print(
                        "Goodbye!"
                    )
                    break
                else:
                    print(
                        "Invalid choice."
                    )
            except ClinicError as error:
                print(
                    f"\nError: {error}"
                )
clinic = ClinicSystem()
clinic.main_menu()