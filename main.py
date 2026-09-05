class Person:
    def __init__(self, person_id, name):
        self.id = person_id
        self.name = name

    def get_info(self):
        return f"ID: {self.id}, Name: {self.name}"


class Patient(Person):
    def __init__(self, person_id, name, age, phone, case_type):
        super().__init__(person_id, name)
        self.age = age
        self.phone = phone
        self.case_type = case_type

    def get_info(self):
        return (
            f"Patient ID: {self.id}, "
            f"Name: {self.name}, "
            f"Age: {self.age}, "
            f"Phone: {self.phone}, "
            f"Case Type: {self.case_type}"
        )


class Doctor(Person):
    def __init__(
            self,
            person_id,
            name,
            specialty,
            schedule
    ):
        super().__init__(person_id, name)
        self.specialty = specialty
        self.schedule = schedule

    def get_info(self):
        schedule_info = []

        for day, hours in self.schedule.items():
            schedule_info.append(
                f"{day}: {hours['start']} - {hours['end']}"
            )

        return (
            f"Doctor ID: {self.id}, "
            f"Name: {self.name}, "
            f"Specialty: {self.specialty}, "
            f"Schedule: {', '.join(schedule_info)}"
        )


class Appointment:
    def __init__(
            self,
            patient,
            doctor,
            day,
            time,
            status="waiting"
    ):
        self.patient = patient
        self.doctor = doctor
        self.day = day
        self.time = time
        self.status = status

    def update_status(self, new_status):
        self.status = new_status

    def get_appointment_info(self):
        return (
            f"Patient: {self.patient.name} | "
            f"Doctor: {self.doctor.name} | "
            f"Day: {self.day} | "
            f"Time: {self.time} | "
            f"Status: {self.status}"
        )

    def find_appointment(
            self,
            patient_id,
            doctor_id,
            appointment_day,
            appointment_time
    ):
        for appointment in self.appointments:
            if (
                    appointment.patient.id == patient_id
                    and appointment.doctor.id == doctor_id
                    and appointment.day == appointment_day
                    and appointment.time == appointment_time
            ):
                return appointment

        return None


class ClinicManager:
    def __init__(self):
        self.patients = []
        self.doctors = []
        self.appointments = []

    def generate_patient_id(self):
        number = len(self.patients) + 1
        return f"P{number:03d}"

    def generate_doctor_id(self):
        number = len(self.doctors) + 1
        return f"D{number:03d}"

    def add_patient(self, patient):
        self.patients.append(patient)

    def add_doctor(self, doctor):
        self.doctors.append(doctor)

    def add_appointment(self, appointment):
        self.appointments.append(appointment)

    def find_patient(self, patient_id):
        for patient in self.patients:
            if patient.id == patient_id:
                return patient
        return None

    def find_doctor(self, doctor_id):
        for doctor in self.doctors:
            if doctor.id == doctor_id:
                return doctor
        return None

    def find_doctors_by_specialty(self, specialty):
        matching_doctors = []

        for doctor in self.doctors:
            if (
                doctor.specialty.lower() == specialty.lower()
            ):
                matching_doctors.append(doctor)

        return matching_doctors

    def find_appointment(self, patient_id, doctor_id, appointment_time):
        for appointment in self.appointments:
            if (
                    appointment.patient.id == patient_id
                    and appointment.doctor.id == doctor_id
                    and appointment.time == appointment_time
            ):
                return appointment
        return None


def register_patient(manager):
    print("\n--- Register Patient ---")

    name = input("Enter patient name: ")
    age = int(input("Enter patient age: "))
    phone = input("Enter patient phone: ")
    case_type = input("Enter case type: ")

    patient_id = manager.generate_patient_id()

    patient = Patient(
        patient_id,
        name,
        age,
        phone,
        case_type
    )

    manager.add_patient(patient)

    print(f"Generated Patient ID: {patient_id}")
    print("Patient registered successfully.")
    print(patient.get_info())

def add_doctor(manager):
    print("\n--- Add Doctor ---")

    doctor_id = manager.generate_doctor_id()
    name = input("Enter doctor name: ")
    specialty = input("Enter specialty: ")

    schedule = {}
    for i in range(3):
        day = input(f"Enter working day {i + 1}: ")

        start_time = input(
            f"Enter start time for {day} (HH:MM): "
        )
        end_time = input(
            f"Enter end time for {day} (HH:MM): "
        )
        schedule[day] = {
            "start": start_time,
            "end": end_time
        }

    working_hours = (
        f"{working_hours_start} - {working_hours_end}"
    )

    doctor = Doctor(
        doctor_id,
        name,
        specialty,
        schedule
    )

    manager.add_doctor(doctor)

    print("Doctor added successfully.")
    print(doctor.get_info())


def create_appointment(manager):
    print("\n--- Book Appointment ---")

    patient_id = input("Enter patient ID: ")

    patient = manager.find_patient(patient_id)

    if patient is None:
        print("Patient not found.")
        return

    specialty = input("Enter required specialty: ")

    doctors = manager.find_doctors_by_specialty(specialty)

    if not doctors:
        print("No doctors found for this specialty.")
        return

    print("\nAvailable Doctors:")

    for index, doctor in enumerate(doctors, start=1):
        print(f"\n{index}. {doctor.name}")

        for day, hours in doctor.schedule.items():
            print(
                f"   {day}: "
                f"{hours['start']} - {hours['end']}"
            )

    doctor_choice = int(
        input("\nChoose doctor number: ")
    )

    if doctor_choice < 1 or doctor_choice > len(doctors):
        print("Invalid doctor choice.")
        return

    doctor = doctors[doctor_choice - 1]

    appointment_day = input(
        "\nEnter appointment day: "
    )

    if appointment_day not in doctor.schedule:
        print("Doctor is not available on this day.")
        return

    working_hours = doctor.schedule[appointment_day]

    print(
        f"Working Hours: "
        f"{working_hours['start']} - "
        f"{working_hours['end']}"
    )

    appointment_time = input(
        "Enter appointment time (HH:MM): "
    )

    start_time = working_hours["start"]
    end_time = working_hours["end"]

    if not (start_time <= appointment_time <= end_time):
        print("Appointment time is outside doctor's working hours.")
        return

    existing_appointment = manager.find_appointment(
        patient.id,
        doctor.id,
        appointment_day,
        appointment_time
    )

    if existing_appointment is not None:
        print("Duplicate booking. Appointment already exists.")
        return

    appointment = Appointment(
        patient,
        doctor,
        appointment_day,
        appointment_time,
        "waiting"
    )

    manager.add_appointment(appointment)

    print("Appointment booked successfully.")
    print(appointment.get_appointment_info())


def update_visit_status(manager):
    print("\n--- Update Visit Status ---")

    patient_id = input("Enter patient ID: ")
    doctor_id = input("Enter doctor ID: ")

    appointment = manager.find_appointment(
        patient_id,
        doctor_id
    )

    if appointment is None:
        print("Appointment not found.")
        return

    print(f"Current status: {appointment.status}")

    new_status = input(
        "Enter new status "
        "(waiting/in progress/completed/cancelled): "
    ).lower()

    appointment.update_status(new_status)

    print("Visit status updated successfully.")
    print(appointment.get_appointment_info())


def show_waiting_queue(manager):
    print("\n--- Waiting Queue ---")

    waiting_appointments = []

    for appointment in manager.appointments:
        if appointment.status == "waiting":
            waiting_appointments.append(appointment)

    if not waiting_appointments:
        print("No patients in the waiting queue.")
        return

    for index, appointment in enumerate(
        waiting_appointments,
        start=1
    ):
        print(
            f"{index}. "
            f"Patient: {appointment.patient.name} | "
            f"Doctor: {appointment.doctor.name} | "
            f"Time: {appointment.time}"
        )


def main_menu(manager):
    while True:
        print("\n===== Smart Clinic Queue System =====")
        print("1. Register Patient")
        print("2. Add Doctor")
        print("3. Book Appointment")
        print("4. Update Visit Status")
        print("5. Show Waiting Queue")
        print("6. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            register_patient(manager)

        elif choice == "2":
            add_doctor(manager)

        elif choice == "3":
            create_appointment(manager)

        elif choice == "4":
            update_visit_status(manager)

        elif choice == "5":
            show_waiting_queue(manager)

        elif choice == "6":
            print("Exiting the system...")
            break

        else:
            print("Invalid choice. Please try again.")


def oop_testing():
    print("\n===== OOP Testing =====")

    patient = Patient(
        "P100",
        "Test Patient",
        25,
        "01012345678",
        "regular"
    )

    doctor = Doctor(
        "D100",
        "Dr. Test",
        "Cardiology",
        {
            "Monday": {
                "start": "09:00",
                "end": "14:00"
            },
            "Wednesday": {
                "start": "09:00",
                "end": "14:00"
            },
            "Saturday": {
                "start": "10:00",
                "end": "15:00"
            }
        }
    )

    appointment = Appointment(
        patient,
        doctor,
        "Monday",
        "10:00"
    )

    manager = ClinicManager()

    manager.add_patient(patient)
    manager.add_doctor(doctor)
    manager.add_appointment(appointment)

    print("\n--- Patient Object ---")
    print(patient.get_info())

    print("\n--- Doctor Object ---")
    print(doctor.get_info())

    print("\n--- Appointment Object ---")
    print(appointment.get_appointment_info())

    print("\n--- Inheritance Test ---")

    if isinstance(patient, Person):
        print("Patient inherits from Person.")

    if isinstance(doctor, Person):
        print("Doctor inherits from Person.")

    print("\n--- Polymorphism Test ---")

    people = [patient, doctor]

    for person in people:
        print(person.get_info())

    print("\n--- Manager Data Test ---")
    print(f"Patients: {len(manager.patients)}")
    print(f"Doctors: {len(manager.doctors)}")
    print(f"Appointments: {len(manager.appointments)}")

    print("\n--- Register Patient Test ---")
    print("Patient can be added through register_patient().")

    print("\n--- Add Doctor Test ---")
    print("Doctor can be added through add_doctor().")

    print("\nOOP testing completed.")





if __name__ == "__main__":
    manager = ClinicManager()

    oop_testing()

    main_menu(manager)