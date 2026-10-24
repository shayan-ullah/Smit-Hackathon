# Execution Commands and Output Evidence

This document records the exact commands executed during the build, automated verification, and demonstration of the Smart Bus Reservation System.

## Environment Details
- **Platform**: Windows (PowerShell)
- **Interpreter**: Python 3.12.12 (`C:\msys64\ucrt64\bin\python.exe`)
- **Dependencies**: Python Standard Library only

---

## 1. Unit Tests Execution (`test_main.py`)
- **Command**: `python -m unittest tests/test_main.py -v`
- **Working Directory**: `project/`
- **Exit Code**: `0`
- **Result Output**:
```text

test_ex01_name_validation (tests.test_main.TestSmartBusCore.test_ex01_name_validation)
EX-01: Reject empty or whitespace-only names; trimmed nonempty name accepted. ... ok
test_ex02_age_validation (tests.test_main.TestSmartBusCore.test_ex02_age_validation)
EX-02: Reject text, 0, negative, decimals, exponents, empty; positive whole age accepted. ... ok
test_ex03_route_validation (tests.test_main.TestSmartBusCore.test_ex03_route_validation)
EX-03: Reject unknown route R999 or empty route ID with no state change. ... ok
test_ex04_seat_quantity_validation (tests.test_main.TestSmartBusCore.test_ex04_seat_quantity_validation)
EX-04: Reject text, -1, 1.5, empty; quantity 1 works. ... ok
test_ex05_case_and_whitespace_id_normalization (tests.test_main.TestSmartBusCore.test_ex05_case_and_whitespace_id_normalization)
EX-05: Normalize route and booking IDs with whitespace and mixed case. ... ok
test_ex06_id_sequence_without_reuse (tests.test_main.TestSmartBusCore.test_ex06_id_sequence_without_reuse)
EX-06: Three valid bookings with cancellation between get B1001, B1002, B1003 without ID reuse. ... ok
test_ex07_collision_avoidance_in_id_allocator (tests.test_main.TestSmartBusCore.test_ex07_collision_avoidance_in_id_allocator)
EX-07: Pre-populate issued set with B1001; next booking automatically skips to B1002. ... ok
test_ex08_cancel_unknown_or_blank_id (tests.test_main.TestSmartBusCore.test_ex08_cancel_unknown_or_blank_id)
EX-08: Cancel unknown or blank ID fails with helpful error; state unchanged. ... ok
test_ex09_state_isolation (tests.test_main.TestSmartBusCore.test_ex09_state_isolation)
EX-09: Independent state instances do not share mutable references. ... ok
test_ex10_empty_bookings_view (tests.test_main.TestSmartBusCore.test_ex10_empty_bookings_view)
EX-10: Empty bookings history prints helpful message without exception. ... ok
test_ex11_route_status_transitions (tests.test_main.TestSmartBusCore.test_ex11_route_status_transitions)
EX-11: Check status transitions: Available -> Partially Booked -> Fully Booked. ... ok
test_ex12_all_routes_exhausted (tests.test_main.TestSmartBusCore.test_ex12_all_routes_exhausted)
EX-12: When all routes are fully booked, available-only view reports none available; all view still shows 5. ... ok
test_ex13_schedule_structure (tests.test_main.TestSmartBusCore.test_ex13_schedule_structure)
EX-13: Schedule displays grouped departures and 'No scheduled departures' for Mirpur Khas and Lahore. ... ok
test_ex14_isolated_report_fixture (tests.test_main.TestSmartBusCore.test_ex14_isolated_report_fixture)
EX-14: Fresh state except R101 available_seats=0 without bookings -> fully_booked=1, revenue=0. ... ok
test_ex15_search_route_id_and_unknown_id (tests.test_main.TestSmartBusCore.test_ex15_search_route_id_and_unknown_id)
EX-15: Search exact route ID 'R104' returns 1 match; search unknown returns empty. ... ok
test_ex16_empty_routes_fixture (tests.test_main.TestSmartBusCore.test_ex16_empty_routes_fixture)
EX-16: Empty routes list in state handled gracefully by views and report. ... ok
test_ex19_reject_bool_and_non_int_types (tests.test_main.TestSmartBusCore.test_ex19_reject_bool_and_non_int_types)
EX-19: Core book_ticket rejects bool values (True/False) and float types for age and seats. ... ok
test_ex20_comprehensive_invariant_reconciliation (tests.test_main.TestSmartBusCore.test_ex20_comprehensive_invariant_reconciliation)
EX-20: State invariants hold throughout a complex sequence of operations. ... ok
test_tc01_initial_routes_and_capacity (tests.test_main.TestSmartBusCore.test_tc01_initial_routes_and_capacity)
TC-01: Starter routes R101-R105 correctly configured with total capacity 183. ... ok
test_tc02_search_hyderabad (tests.test_main.TestSmartBusCore.test_tc02_search_hyderabad)
TC-02: Search 'hyderabad' returns R101, R103, R105 in order; case & spaces handled. ... ok
test_tc03_search_unknown_city (tests.test_main.TestSmartBusCore.test_tc03_search_unknown_city)
TC-03: Search 'Atlantis' yields empty results without mutating state. ... ok
test_tc04_valid_booking_ahmed (tests.test_main.TestSmartBusCore.test_tc04_valid_booking_ahmed)
TC-04: Book Ahmed, 24, R101, 2 seats -> B1001, Rs. 2400, R101 avail 38, ID tracked. ... ok
test_tc05_reject_zero_seats (tests.test_main.TestSmartBusCore.test_tc05_reject_zero_seats)
TC-05: Attempt booking with 0 seats -> rejected with no state change. ... ok
test_tc06_reject_excess_seats (tests.test_main.TestSmartBusCore.test_tc06_reject_excess_seats)
TC-06: Attempt booking 41 seats on fresh R101 (capacity 40) -> rejected, no state change. ... ok
test_tc07_cancel_confirmed_booking (tests.test_main.TestSmartBusCore.test_tc07_cancel_confirmed_booking)
TC-07: Cancel confirmed B1001 -> seats restored to 40, status Cancelled, retained in history. ... ok
test_tc08_reject_repeat_cancellation (tests.test_main.TestSmartBusCore.test_tc08_reject_repeat_cancellation)
TC-08: Repeat cancellation of B1001 -> rejected, no extra seats added. ... ok
test_tc09_report_on_fresh_state (tests.test_main.TestSmartBusCore.test_tc09_report_on_fresh_state)
TC-09: Generate report on empty state -> all booking totals and revenue zero. ... ok
test_tc10_book_all_seats_on_route (tests.test_main.TestSmartBusCore.test_tc10_book_all_seats_on_route)
TC-10: Book all 40 seats on R101 -> Rs. 48000, Fully Booked, next request rejected. ... ok
test_tc11_two_bookings_and_cancel_one (tests.test_main.TestSmartBusCore.test_tc11_two_bookings_and_cancel_one)
TC-11: Two bookings, cancel one -> report reflects only Confirmed revenue/seats. ... ok

----------------------------------------------------------------------
Ran 29 tests in 0.007s

OK
```

---

## 2. CLI and Navigation Tests Execution (`test_cli.py`)
- **Command**: `python -m unittest tests/test_cli.py -v`
- **Working Directory**: `project/`
- **Exit Code**: `0`
- **Result Output**:
```text

test_cli_booking_flow_success_and_failure (tests.test_cli.TestSmartBusCLI.test_cli_booking_flow_success_and_failure)
CLI booking helper handles valid flow, parse errors, and business rule failures. ... ok
test_cli_cancellation_flow (tests.test_cli.TestSmartBusCLI.test_cli_cancellation_flow)
CLI cancellation handles valid cancellation and error conditions. ... ok
test_cli_search_flow (tests.test_cli.TestSmartBusCLI.test_cli_search_flow)
CLI search handles blank input, found matches, and not found. ... ok
test_deterministic_demo_session_mocked (tests.test_cli.TestSmartBusCLI.test_deterministic_demo_session_mocked)
Execute the exact 9-step deterministic workflow from 06_ACCEPTANCE_TESTS.md via mocked CLI input. ... ok
test_ex17_eof_and_keyboard_interrupt_handling (tests.test_cli.TestSmartBusCLI.test_ex17_eof_and_keyboard_interrupt_handling)
EX-17: EOFError and KeyboardInterrupt during menu or booking exit gracefully without traceback. ... ok
test_ex18_invalid_submenu_then_back (tests.test_cli.TestSmartBusCLI.test_ex18_invalid_submenu_then_back)
EX-18: Invalid submenu choice in Option 1 and Option 6 shows error, repeats, and returns safely on 0. ... ok
test_ex21_fresh_process_has_independent_state (tests.test_cli.TestSmartBusCLI.test_ex21_fresh_process_has_independent_state)
EX-21: Starting a new session begins with initial capacity, empty history, and B1001 candidate. ... ok
test_subprocess_execution (tests.test_cli.TestSmartBusCLI.test_subprocess_execution)
Execute main.py in a real subprocess using sys.executable to verify end-to-end OS execution. ... ok
test_tc12_invalid_menu_choices_and_exit (tests.test_cli.TestSmartBusCLI.test_tc12_invalid_menu_choices_and_exit)
TC-12: Main choice 'abc', '0', '9', then '8' -> helpful errors, repeated menu, clean exit. ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.158s

OK
```

---

## 3. Deterministic Demonstration Console Run
- **Command**: `python main.py` (with piped deterministic standard input)
- **Working Directory**: `project/`
- **Exit Code**: `0`
- **Input Sequence**:
  1. Option `1` -> Submenu `1` (View All Routes) -> `0` (Back)
  2. Option `3` -> `Ahmed`, `24`, `R101`, `2` (Book 2 seats on R101)
  3. Option `3` -> `Sara`, `30`, `R102`, `3` (Book 3 seats on R102)
  4. Option `5` -> `B1001` (Cancel B1001)
  5. Option `5` -> `B1001` (Attempt repeat cancellation -> rejected)
  6. Option `7` -> Generate Booking Report (Reconciliation: 2 total, 1 confirmed, 1 cancelled, 3 reserved seats, Rs. 6000 revenue)
  7. Option `4` -> View My Bookings (Inspect B1001 Cancelled and B1002 Confirmed)
  8. Option `1` -> Submenu `3` (View Schedule by Departure City) -> `0` (Back)
  9. Option `8` -> Clean exit
- **Observed Transcript**: Full transcript saved in `evidence/demo-session.txt`.

---

## 4. Portability Verification Command (Directory with Spaces)
- **Command**: `python -m unittest discover -s tests -v`
- **Working Directory**: `C:\Users\DELL\.gemini\antigravity\brain\c21932f3-1293-41fc-a6d7-5e49948d49b4\scratch\test smart bus with spaces`
- **Exit Code**: `0`
- **Result Output**:
```text
Ran 38 tests in 0.111s

OK
```
- **App Startup Command**: `python -c "import subprocess, sys; p = subprocess.run([sys.executable, 'main.py'], input='8\n', capture_output=True, text=True); print('Exit code:', p.returncode); print('Output contains welcome:', 'Welcome to Smart Bus' in p.stdout)"`
- **Exit Code**: `0` (Output contains welcome: True)
- **Cleanup**: Temporary test directory removed from scratch path after verification.
