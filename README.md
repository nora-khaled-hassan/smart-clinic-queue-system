# 🏥 Smart Clinic Queue System

A console-based **Smart Clinic Queue System** built with Python and JSON
persistence.

The project manages patients, doctors, nurses, appointments, payments,
bills, clinical visits, queue priorities, authentication, and reports
through role-based dashboards.

------------------------------------------------------------------------

## 📌 Project Overview

The system is designed as a small clinic management application with
four main user roles:

-   👑 **Admin**
-   🧑‍⚕️ **Doctor**
-   👩‍⚕️ **Nurse**
-   🧑‍💼 **Patient**

Each role has its own dashboard and permitted operations.

The application stores its data in a JSON file and automatically saves
important state changes.

------------------------------------------------------------------------

## 🛠️ Technologies Used

  -----------------------------------------------------------------------
  Technology                          Usage
  ----------------------------------- -----------------------------------
  🐍 Python                           Main programming language

  📄 JSON                             Persistent data storage

  🔐 `hashlib`                        SHA-256 password hashing

  🕒 `datetime`                       Dates, times, timestamps, working
                                      hours

  🎲 `random`                         Appointment payment codes and
                                      confirmation numbers

  🔎 `re`                             ID, phone, and time validation

  📁 `pathlib`                        Safe JSON file replacement

  🧩 `typing`                         Type hints such as `List` and
                                      `Optional`

  ♻️ `functools.reduce`               Revenue calculation

  🔧 OOP                              Classes for users, appointments,
                                      payments, visits, and managers
  -----------------------------------------------------------------------

The project uses Python's standard library and does not require external
packages.

------------------------------------------------------------------------

## 🚀 How to Run

Make sure Python 3 is installed.

Run:

``` bash
python smart_clinic_system_updated_v2.py
```

The program starts with:

``` text
====================================
         SMART CLINIC SYSTEM
====================================
1. Login
2. Register Patient
3. Quit
```

------------------------------------------------------------------------

## 🔐 Authentication

Users log in using:

``` text
ID + Password
```

Supported ID formats:

  Role         ID Format   Example
  ------------ ----------- ---------
  👑 Admin     `A###`      `A001`
  🧑‍💼 Patient   `P###`      `P001`
  🧑‍⚕️ Doctor    `D###`      `D001`
  👩‍⚕️ Nurse     `N###`      `N001`

### Password Hashing

Passwords are hashed with SHA-256 before being stored:

``` python
hashlib.sha256(password.encode("utf-8")).hexdigest()
```

The JSON file stores the hash rather than the original password.

Example format:

``` text
240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
```

During login, the entered password is hashed again and compared with the
stored hash.

------------------------------------------------------------------------

## 👑 Default Admin

The system automatically creates a default admin if `A001` does not
already exist.

``` text
ID: A001
Password: admin123
Role: admin
```

The password is stored as a SHA-256 hash.

------------------------------------------------------------------------

# 👥 User Roles

## 👑 Admin

Admin can:

-   Add doctors
-   Add nurses
-   Remove doctors
-   Generate daily reports
-   View emergency cases
-   View doctor revenue
-   View completed visits
-   Save data
-   Logout

Admin menu:

``` text
1. Add Doctor
2. Add Nurse
3. Remove Doctor
4. Daily Report
5. Emergency Cases Report
6. Doctor Revenue Report
7. Completed Visits Report
8. Save Data
9. Logout
```

------------------------------------------------------------------------

## 🧑‍💼 Patient

Patients can:

-   Book appointments
-   Pay for appointments
-   View their appointments
-   Logout

Patient menu:

``` text
1. Book Appointment
2. Pay for Appointment
3. View My Appointments
4. Logout
```

------------------------------------------------------------------------

## 👩‍⚕️ Nurse

Nurses can:

-   View assigned doctors' appointments
-   Check in patients
-   Assign case priority
-   View the waiting queue
-   View emergency cases
-   Logout

Nurse menu:

``` text
1. View Assigned Doctor's Appointments
2. Check-In Patient
3. View Waiting Queue
4. View Emergency Cases
5. Logout
```

------------------------------------------------------------------------

## 🧑‍⚕️ Doctor

Doctors can:

-   Call the next patient
-   Enter clinical assessment
-   Add doctor notes
-   Complete a visit
-   Add prescriptions
-   Logout

Doctor menu:

``` text
1. Call Next Patient
2. Enter Clinical Assessment
3. Complete Current Visit
4. Logout
```

------------------------------------------------------------------------

# 📅 Appointment Management

Appointments contain:

-   Appointment ID
-   Patient
-   Doctor
-   Date
-   Time
-   Service type
-   Status
-   Case type
-   Priority
-   Payment status
-   Payment code
-   Confirmation number
-   Amount

Appointment IDs follow:

``` text
AP001
AP002
AP003
...
```

------------------------------------------------------------------------

## 🩺 Service Types

The system supports three service types:

  Service          Base Rate
  -------------- -----------
  Consultation           2.5
  Examination           3.75
  Emergency             6.75

The appointment amount is calculated using:

``` text
Base Service Rate × Doctor Rate
```

------------------------------------------------------------------------

# ⏰ Doctor Availability

Doctors can have:

-   Working days
-   Start time
-   End time
-   Appointment duration
-   Availability status
-   Assigned nurses

The system checks the requested appointment time against the doctor's
working schedule.

------------------------------------------------------------------------

# 🚫 Appointment Validation

The system checks:

-   Patient existence
-   Doctor existence
-   Valid time format
-   Doctor working days
-   Doctor working hours
-   Duplicate patient booking
-   Doctor time-slot conflicts

Time format:

``` text
HH:MM
```

Example:

``` text
10:30
```

------------------------------------------------------------------------

# 💳 Payment System

Each appointment receives a randomly generated **12-digit payment
code**.

Example:

``` text
Payment Code: 123456789012
```

After successful payment, the system generates a random **10-digit
confirmation number**.

Example:

``` text
Confirmation: 1234567890
```

Payment states include:

``` text
PENDING
PAID
FAILED
```

Appointment payment status includes:

``` text
UNPAID
PAID
```

The system prevents paying for an appointment twice.

------------------------------------------------------------------------

# 🧾 Billing

A bill is generated for a paid appointment.

The bill contains:

-   Patient
-   Doctor
-   Service type
-   Base rate
-   Doctor rate
-   Total amount
-   Payment status
-   Appointment ID

------------------------------------------------------------------------

# 🚑 Clinical Triage

Patients are assigned a priority during check-in.

  Case Type      Priority
  -------------- ----------
  🚨 Emergency   P1
  ⚠️ Urgent      P2
  🟢 Regular     P3

The queue is sorted by:

1.  Priority
2.  Arrival time

Therefore, higher-priority cases are called first.

------------------------------------------------------------------------

# 🧑‍⚕️ Clinical Visits

A visit is created when a doctor calls a waiting patient.

Each visit stores:

-   Visit ID
-   Appointment
-   Patient
-   Doctor
-   Diagnosis
-   Doctor notes
-   Prescription
-   Vital signs
-   Nurse notes
-   Status
-   Created time
-   Completed time

Visit IDs follow:

``` text
V0001
V0002
V0003
...
```

Visit states include:

``` text
IN_PROGRESS
COMPLETED
```

------------------------------------------------------------------------

# 📊 Reports

The Admin dashboard provides:

## 📅 Daily Clinic Report

The report includes:

-   Date
-   Total patients
-   Completed visits
-   Waiting patients
-   Cancelled appointments
-   Emergency cases
-   Urgent cases
-   Regular cases
-   Doctors working
-   Nurses working
-   Paid appointments
-   Unpaid appointments
-   Total revenue

------------------------------------------------------------------------

## 🚨 Emergency Cases Report

Displays patients currently classified as emergency cases (`P1`).

------------------------------------------------------------------------

## 💰 Doctor Revenue Report

Calculates paid revenue for each doctor and sorts doctors by revenue.

------------------------------------------------------------------------

## ✅ Completed Visits Report

Displays completed visits with:

-   Visit ID
-   Patient
-   Diagnosis

------------------------------------------------------------------------

# 💾 JSON Persistence

The application uses:

``` text
clinic_data.json
```

The JSON stores:

``` text
users
patients
doctors
nurses
appointments
visits
bills
payments
waiting_queue
action_history
settings
```

Important state changes are automatically saved.

The save process writes to a temporary JSON file first and then replaces
the original file.

This helps reduce the risk of leaving a partially written JSON file.

------------------------------------------------------------------------

# 🔄 Data Loading

When the application starts, it loads saved data from:

``` text
clinic_data.json
```

The system restores:

-   Users
-   Patients
-   Doctors
-   Nurses
-   Appointments
-   Payments
-   Bills
-   Visits
-   Waiting queue
-   Action history

Appointment and visit counters are also updated based on existing IDs.

------------------------------------------------------------------------

# 🔐 Password Migration

If the JSON contains an old password that is not already a 64-character
SHA-256 hexadecimal hash, the system hashes it automatically and saves
the migrated data.

This allows older JSON data to be converted to the hashed-password
format.

------------------------------------------------------------------------

# 🧪 Validation Rules

## 📱 Phone Number

The system validates Egyptian-style mobile numbers using:

``` text
01[0125]XXXXXXXX
```

Example:

``` text
01012345678
```

------------------------------------------------------------------------

## 🎂 Age

Age must be:

``` text
1 - 120
```

------------------------------------------------------------------------

## 🔑 Password

Passwords must contain at least:

``` text
4 characters
```

------------------------------------------------------------------------

## 🆔 IDs

IDs are generated automatically:

``` text
Patient  → P001
Doctor   → D001
Nurse    → N001
Admin    → A001
```

------------------------------------------------------------------------

# 🧱 Main Classes

The project is organized using object-oriented programming.

### 👤 Person

Base class for common person information:

-   ID
-   Name
-   Phone

### 🧑‍💼 Patient

Extends `Person`.

Stores:

-   Age
-   Case type
-   Priority
-   Appointments

### 🧑‍⚕️ Doctor

Extends `Person`.

Stores:

-   Specialty
-   Rate
-   Appointment duration
-   Working days
-   Working hours
-   Availability
-   Assigned nurses

### 👩‍⚕️ Nurse

Extends `Person`.

Stores:

-   Assigned doctors
-   Availability

### 📅 Appointment

Handles appointment information and status.

### 💳 Payment

Handles payment processing and confirmation numbers.

### 🧾 Bill

Represents appointment billing information.

### 🏥 AppointmentManager

Handles:

-   Appointment creation
-   Appointment lookup
-   Doctor availability
-   Duplicate bookings
-   Payments
-   Bills
-   Appointment iteration

### 🚑 Visit

Stores clinical visit information.

### 🚦 ClinicalQueueManager

Handles:

-   Patient check-in
-   Triage priority
-   Waiting queue
-   Emergency filtering
-   Starting visits

### 🏥 ClinicManager

Acts as the main system manager.

It connects:

-   Users
-   Patients
-   Doctors
-   Nurses
-   Appointments
-   Payments
-   Bills
-   Queue
-   Visits
-   Reports
-   JSON persistence

------------------------------------------------------------------------

# 🧠 Python Concepts Used

The project demonstrates several Python concepts:

### 🏗️ Object-Oriented Programming

Used through:

``` python
class Person
class Patient
class Doctor
class Nurse
class Appointment
class Payment
class Bill
class Visit
class AppointmentManager
class ClinicalQueueManager
class ClinicManager
```

### 🧬 Inheritance

``` text
Person
 ├── Patient
 ├── Doctor
 └── Nurse
```

### ⚠️ Custom Exceptions

Examples:

``` text
InvalidIDError
InvalidPhoneError
DuplicateUserError
UserNotFoundError
WrongPasswordError
AppointmentError
InvalidAppointmentTimeError
DoctorUnavailableError
DuplicateBookingError
PatientNotFoundError
DoctorNotFoundError
InvalidPaymentError
AppointmentNotFoundError
PatientAlreadyCheckedInError
```

### 🔎 Regular Expressions

Used for:

-   ID validation
-   Phone validation
-   Time validation
-   Detecting numeric parts of generated IDs

### 🔁 Functional Programming

The project uses:

``` python
map()
filter()
reduce()
lambda
```

For example, revenue is calculated using `map()` and `reduce()`.

### 🧩 Type Hints

Examples:

``` python
List[Appointment]
Optional[Appointment]
```

### 📁 File Handling

JSON data is read and written using Python file operations.

------------------------------------------------------------------------

# 🗂️ Project Structure

A simple project setup can be:

``` text
Smart-Clinic/
│
├── smart_clinic_system_updated_v2.py
├── clinic_data.json
└── README.md
```

### `smart_clinic_system_updated_v2.py`

Main Python application.

### `clinic_data.json`

Persistent application data.

### `README.md`

Project documentation.

------------------------------------------------------------------------

# ▶️ Basic Usage Flow

``` text
🏥 Start Program
       ↓
🔐 Login / Register
       ↓
👤 Select User Role
       ↓
┌───────────────┐
│ Admin         │
│ Patient       │
│ Doctor        │
│ Nurse         │
└───────────────┘
       ↓
📅 Manage Appointments
       ↓
💳 Payment
       ↓
🚑 Check-In
       ↓
🚦 Queue Priority
       ↓
🧑‍⚕️ Clinical Visit
       ↓
📊 Reports
       ↓
💾 JSON Persistence
```

------------------------------------------------------------------------

# 🧪 Example Test Data

## Patient Registration

``` text
Name: Mariam Ahmed
Phone: 01012345678
Age: 22
Password: mariam123
```

## Admin Login

``` text
ID: A001
Password: admin123
```

## Doctor Example

``` text
Name: Ahmed Ali
Specialty: Cardiology
Phone: 01011112222
Rate: 2
Appointment Duration: 30
Working Days: Monday,Tuesday,Wednesday,Thursday,Friday
Start: 09:00
End: 15:00
Password: doctor123
```

## Nurse Example

``` text
Name: Sara Ahmed
Phone: 01022223333
Assigned Doctor: D001
Password: nurse123
```

------------------------------------------------------------------------

# 🔒 Security Note

The project uses **SHA-256 hashing** for password storage rather than
reversible encryption.

The original password is not needed to verify login: the entered
password is hashed and compared with the stored hash.

For a production medical system, additional security controls would be
required, such as stronger password policies, salted password hashing
with a password-specific algorithm, authorization hardening, encrypted
transport/storage, audit controls, and protection of sensitive medical
data.

------------------------------------------------------------------------

# 📝 Project Tasks

The source code is organized around the project task ownership:

-   👩‍💻 **Task Person 1: Noura** --- validation, password hashing, base
    person classes
-   👩‍💻 **Task Person 2: Aya** --- appointments, payments, bills
-   👩‍💻 **Task Person 3: Kholoud** --- visits, triage, clinical queue
-   👩‍💻 **Task Person 4: ClinicManager** --- system integration,
    authentication, persistence, dashboards, reports

------------------------------------------------------------------------

# 📌 Important Notes

-   The application is console-based.
-   Data is stored locally in JSON.
-   IDs are generated automatically.
-   Passwords are stored as SHA-256 hashes.
-   Important changes are automatically saved.
-   Appointment availability depends on doctor working days and hours.
-   Queue priority is based on Emergency, Urgent, and Regular cases.
-   Payment is required before patient check-in.
-   A doctor must call a patient before entering an assessment or
    completing a visit.

------------------------------------------------------------------------

# 🏁 Conclusion

**Smart Clinic Queue System** combines:

🏥 Clinic Management\
👥 Role-Based Users\
📅 Appointment Scheduling\
💳 Payments\
🧾 Billing\
🚑 Triage\
🚦 Priority Queue\
🧑‍⚕️ Clinical Visits\
📊 Reports\
🔐 Password Hashing\
💾 JSON Persistence\
🧱 Object-Oriented Programming

It provides a complete console-based workflow for managing a small
clinic from registration and appointment booking through payment,
check-in, queue management, clinical visits, and reporting.
