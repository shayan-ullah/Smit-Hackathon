# Smart Bus Ticket Booking & Reservation System

A portable, beginner-friendly, single-user Python 3 text-console application for managing bus routes, seat reservations, cancellations, schedules, and reconciliation reports.

> **CRITICAL NOTICE: IN-MEMORY DATA ONLY**  
> All route modifications, bookings, and cancellation records are stored strictly in-memory during the running process. When the application exits, all booking history is lost and route availability resets to initial values. The system deliberately uses no external database, file storage, or cloud persistence.

---

## 1. System Requirements & Setup

- **Language**: Python 3.10+ (Tested with Python 3.12.12 on Windows 64-bit AMD64).
- **Dependencies**: None. Only the Python Standard Library (`copy`, `io`, `sys`, `unittest`, `unittest.mock`, `pathlib`, `subprocess`) is used.
- **Portability**: Completely portable across Windows, macOS, and Linux. No third-party packages, API keys, databases, network connections, or elevated permissions required.

---

## 2. How to Run the Application and Tests

Always run commands from the `project/` root directory.

### Windows (PowerShell / Command Prompt)

```powershell
# Run the interactive console application
python main.py

# Run all automated tests
python -m unittest discover -s tests -v

# Run verification & evidence generator
python tools/generate_evidence.py
```

### macOS / Linux (Terminal)

```bash
# Run the interactive console application
python3 main.py

# Run all automated tests
python3 -m unittest discover -s tests -v

# Run verification & evidence generator
python3 tools/generate_evidence.py
```

---

## 3. Main Menu & Navigation Guide

The console application features the exact eight-option main menu required by the Product Requirements Document (PRD):

```text
================================
  SMART BUS RESERVATION SYSTEM  
================================
1. View Available Routes
2. Search for a Route
3. Book a Ticket
4. View My Bookings
5. Cancel a Booking
6. View Seat Availability
7. Generate Booking Report
8. Exit
================================
```

### Option Submenus & Features

1. **Option 1 — View Available Routes**:
   - `1`: View all routes (shows sequence, route ID, journey, departure time, fare, seat capacity `available/total`, and status).
   - `2`: View routes with available seats only (skips fully booked routes using `continue`).
   - `3`: View route schedule grouped by departure city (uses nested loops over supported cities and routes; cities without departing routes show `No scheduled departures.`).
   - `0`: Return to main menu.

2. **Option 2 — Search for a Route**:
   - Prompts for route ID (e.g., `R101`) or city name (e.g., `Hyderabad`).
   - Case-insensitive search with outer whitespace stripping.
   - Matching route ID breaks immediately on unique match; city search returns all journeys matching either departure or destination city.

3. **Option 3 — Book a Ticket**:
   - Collects: Passenger Name, Passenger Age, Route ID, Number of Seats.
   - Strict validate-before-mutate policy: rejects empty name, non-positive integer age, unknown route, non-positive seat count, or requests exceeding available seats without modifying state.
   - Automatically allocates a unique booking ID (e.g., `B1001`), calculates fare (fare = unit price × seats in integer rupees), updates availability once, and stores the confirmed booking.

4. **Option 4 — View My Bookings**:
   - Lists all booking records in the current session (both `Confirmed` and `Cancelled`) with sequence numbers.
   - Displays `No bookings found.` if no bookings exist.

5. **Option 5 — Cancel a Booking**:
   - Prompts for Booking ID (e.g., `B1001`).
   - Cancels only an existing `Confirmed` booking; sets status to `Cancelled` and restores seats to the route once.
   - Repeated cancellation attempts or invalid IDs are rejected without extra seat restoration or state corruption.

6. **Option 6 — View Seat Availability**:
   - `1`: View seat availability for all routes with statuses (`Available`, `Partially Booked`, `Fully Booked`).
   - `2`: View seat availability for routes with seats remaining only.
   - `0`: Return to main menu.

7. **Option 7 — Generate Booking Report**:
   - Computes: Total Bookings, Confirmed Bookings, Cancelled Bookings, Seats Reserved (Confirmed only), Confirmed Revenue (Confirmed only, integer Rs.), and Fully Booked Routes.
   - Displays a per-route breakdown grouped via nested loops.
   - Empty sessions safely report 0 totals without exceptions.

8. **Option 8 — Exit**:
   - Cleanly terminates the program loop with an in-memory reset reminder.
   - Safe signal handling: pressing `Ctrl+C` or sending EOF terminates gracefully with no Python traceback.

---

## 4. Starter Routes Fixture (PRD Page 6)

The system initializes with five baseline routes (total capacity: 183 seats):

| Route ID | Departure City | Destination City | Departure Time | Ticket Price | Total Seats | Available Seats | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **R101** | Karachi | Hyderabad | 08:00 AM | Rs. 1,200 | 40 | 40 | Available |
| **R102** | Karachi | Sukkur | 09:30 AM | Rs. 2,000 | 36 | 36 | Available |
| **R103** | Hyderabad | Mirpur Khas | 11:00 AM | Rs. 800 | 32 | 32 | Available |
| **R104** | Karachi | Lahore | 07:00 PM | Rs. 5,000 | 45 | 45 | Available |
| **R105** | Sukkur | Hyderabad | 02:00 PM | Rs. 1,500 | 30 | 30 | Available |

Supported cities tuple: `('Karachi', 'Hyderabad', 'Sukkur', 'Mirpur Khas', 'Lahore')`.

---

## 5. Deterministic Demonstration Session & Reconciliation

A complete sample workflow was executed to verify state transitions and financial reconciliation:

1. **View All Routes**: Initial seats R101=40, R102=36, total=183.
2. **Book Ahmed**: Age 24, R101, 2 seats -> ID `B1001`, Fare Rs. 2,400, R101 seats drop to 38.
3. **Book Sara**: Age 30, R102, 3 seats -> ID `B1002`, Fare Rs. 6,000, R102 seats drop to 33.
4. **Cancel B1001**: Restores 2 seats to R101 (seats back to 40); status becomes `Cancelled`.
5. **Cancel B1001 Again**: Rejected (`already cancelled`); R101 remains at 40 seats.
6. **Booking Report**:
   - Total Bookings: `2`
   - Confirmed Bookings: `1` (Sara)
   - Cancelled Bookings: `1` (Ahmed)
   - Seats Reserved: `3` (Sara only)
   - Confirmed Revenue: `Rs. 6000` (Sara only; Ahmed's Rs. 2,400 excluded)
   - Fully Booked Routes: `0`
7. **View My Bookings**: Displays `B1001` (`Cancelled`) and `B1002` (`Confirmed`).
8. **View Schedule**: Karachi has R101/R102/R104, Hyderabad has R103, Sukkur has R105; Mirpur Khas and Lahore display `No scheduled departures.`
9. **Exit**: Process ends cleanly. Starting a new process proves state resets to 183 seats and 0 bookings.

---

## 6. Execution Evidence

Actual execution logs and screenshots are preserved in `evidence/`:
- `evidence/commands.md`: Commands executed with exit codes and raw console captures.
- `evidence/unit-tests.txt`: Unit test run results (29 tests passing).
- `evidence/cli-tests.txt`: CLI test run results (9 tests passing).
- `evidence/demo-session.txt`: Complete deterministic session transcript.
- `evidence/routes.png`: Rendered capture of Option 1 (Available routes).
- `evidence/booking.png`: Rendered capture of Option 3 (Booking confirmation).
- `evidence/cancellation.png`: Rendered capture of Option 5 (Cancellation & repeat rejection).
- `evidence/report.png`: Rendered capture of Option 7 (Reconciled report).
- `test_cases.txt`: Detailed verification log covering all 34 acceptance scenarios (TC-01..TC-12, EX-01..EX-22).

---

## 7. Scope Boundaries & Exclusions

In accordance with the PRD baseline specification:
- **Included**: In-memory state, exact 8-option menu, route browsing/search/schedules, validate-before-mutate booking, unique IDs, booking history, one-time seat restoration, availability status classification, and aggregated reports.
- **Excluded**: Web interface, GUI, external database, persistent files, online payments, user authentication/passwords, multi-tenancy, age-based fare discounts, bulk seat discounts, individual seat numbering, or optional PRD extensions.
