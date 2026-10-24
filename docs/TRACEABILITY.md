# Traceability Matrix: Requirements, Business Rules, and Test Cases

This document maps all functional requirements (RQ), business rules (BR), and test cases (TC / EX) to their verified implementation in `main.py`, automated tests in `tests/`, and execution evidence in `evidence/`.

---

## 1. Functional Requirements Coverage (RQ-01 to RQ-18)

| Req ID | Requirement Summary | Implementation in `main.py` | Automated Test Verification | Evidence Location |
| --- | --- | --- | --- | --- |
| **RQ-01** | Python 3 console app, single passenger/operator interface, in-memory state resetting on exit | `create_state()`, `main()` | `test_ex09_state_isolation`, `test_ex21_fresh_process_has_independent_state` | `evidence/commands.md`, `evidence/demo-session.txt` |
| **RQ-02** | Exact 8-option main menu with safe invalid handling and clean exit | `main()` menu loop & input dispatch | `test_tc12_invalid_menu_choices_and_exit`, `test_ex17_eof_and_keyboard_interrupt_handling` | `evidence/cli-tests.txt`, `evidence/demo-session.txt` |
| **RQ-03** | Descriptive results, valid empty states, no external dependencies or screen clears | `show_bookings()`, `show_routes()`, `show_report()` | `test_tc09_report_on_fresh_state`, `test_ex10_empty_bookings_view`, `test_ex16_empty_routes_fixture` | `evidence/unit-tests.txt`, `test_cases.txt` |
| **RQ-04** | Starter routes fixture R101-R105 (cap 183), supported cities tuple, issued ID set | `create_state()`, `SUPPORTED_CITIES` | `test_tc01_initial_routes_and_capacity`, `test_ex06_id_sequence_without_reuse` | `evidence/routes.png`, `evidence/unit-tests.txt` |
| **RQ-05** | Formatted route list showing details, enumerate(), and available-only filter using continue | `show_routes()`, `handle_view_routes_menu()` | `test_tc01_initial_routes_and_capacity`, `test_tc10_book_all_seats_on_route`, `test_ex12_all_routes_exhausted` | `evidence/routes.png`, `evidence/unit-tests.txt` |
| **RQ-06** | Search by route ID (break on match) or city (case-insensitive, all matches) | `search_routes()`, `handle_search_route()` | `test_tc02_search_hyderabad`, `test_tc03_search_unknown_city`, `test_ex15_search_route_id_and_unknown_id` | `evidence/unit-tests.txt`, `evidence/cli-tests.txt` |
| **RQ-07** | Input validation for name, positive integer age, existing route, positive seats, available seats | `parse_positive_integer()`, `book_ticket()` | `test_tc05_reject_zero_seats`, `test_tc06_reject_excess_seats`, `test_ex01` to `test_ex04` | `evidence/unit-tests.txt`, `test_cases.txt` |
| **RQ-08** | Sequential IDs beginning B1001, issued ID tracking, integer rupee fare = price * seats | `book_ticket()` | `test_tc04_valid_booking_ahmed`, `test_ex06_id_sequence_without_reuse`, `test_ex07_collision_avoidance_in_id_allocator` | `evidence/booking.png`, `test_cases.txt` |
| **RQ-09** | Detailed booking confirmation matching PRD sample format | `handle_booking()` | `test_tc04_valid_booking_ahmed`, `test_cli_booking_flow_success_and_failure` | `evidence/booking.png`, `evidence/demo-session.txt` |
| **RQ-10** | View My Bookings with enumerate(), shows confirmed and cancelled records | `show_bookings()` | `test_tc11_two_bookings_and_cancel_one`, `test_ex10_empty_bookings_view` | `evidence/demo-session.txt`, `test_cases.txt` |
| **RQ-11** | Cancel booking by ID: restores seats once, retains record, sets status Cancelled | `cancel_booking()`, `handle_cancellation()` | `test_tc07_cancel_confirmed_booking`, `test_tc08_reject_repeat_cancellation`, `test_ex08_cancel_unknown_or_blank_id` | `evidence/cancellation.png`, `test_cases.txt` |
| **RQ-12** | Seat availability view, 3-tier status (Available, Partially Booked, Fully Booked), filter | `show_availability()`, `route_status()` | `test_ex11_route_status_transitions`, `test_tc10_book_all_seats_on_route` | `evidence/unit-tests.txt`, `test_cases.txt` |
| **RQ-13** | Booking report with 6 aggregate totals; Confirmed only for reserved seats and revenue | `build_report()`, `show_report()` | `test_tc09_report_on_fresh_state`, `test_tc11_two_bookings_and_cancel_one`, `test_ex14_isolated_report_fixture` | `evidence/report.png`, `test_cases.txt` |
| **RQ-14** | Per-route report aggregation using nested routes-outer / bookings-inner loops | `build_report()` | `test_tc11_two_bookings_and_cancel_one`, `test_ex20_comprehensive_invariant_reconciliation` | `evidence/report.png`, `evidence/unit-tests.txt` |
| **RQ-15** | Route schedule grouped by departure city using nested loops under Option 1 | `show_schedule()`, `handle_view_routes_menu()` | `test_ex13_schedule_structure` | `evidence/demo-session.txt`, `evidence/unit-tests.txt` |
| **RQ-16** | Meaningful usage and documentation of all required beginner Python concepts | `main.py` (all functions) | `test_main.py`, `test_cli.py`, concept audit | `docs/TECHNICAL_GUIDE.md` |
| **RQ-17** | Complete deliverables: source, tests, evidence captures, README, docs, test_cases.txt | `project/` directory tree | End-to-end verification via `tools/generate_evidence.py` | `DELIVERY_REPORT.md`, `project/` root |
| **RQ-18** | Scope boundary preservation: standard library only, in-memory only, no extra extensions | `project/main.py` | Dependency audit, `test_subprocess_execution` | `project/README.md`, `DELIVERY_REPORT.md` |

---

## 2. Business Rules Coverage (BR-01 to BR-15)

| Rule ID | Business Rule Definition | Implementation | Verified Test Method | Status |
| --- | --- | --- | --- | --- |
| **BR-01** | Passenger name required; reject blank | `book_ticket()` | `test_ex01_name_validation` | PASS |
| **BR-02** | Age must be positive integer | `parse_positive_integer()`, `book_ticket()` | `test_ex02_age_validation`, `test_ex19_reject_bool_and_non_int_types` | PASS |
| **BR-03** | Route must exist in inventory | `book_ticket()`, `find_route()` | `test_ex03_route_validation` | PASS |
| **BR-04** | Seat quantity must be positive integer | `parse_positive_integer()`, `book_ticket()` | `test_tc05_reject_zero_seats`, `test_ex04_seat_quantity_validation`, `test_ex19` | PASS |
| **BR-05** | Requested seats <= available seats | `book_ticket()` | `test_tc06_reject_excess_seats`, `test_tc10_book_all_seats_on_route` | PASS |
| **BR-06** | Booking IDs must be unique | `book_ticket()`, candidate loop | `test_ex06_id_sequence_without_reuse`, `test_ex07_collision_avoidance_in_id_allocator` | PASS |
| **BR-07** | Total fare = unit price * seats | `book_ticket()` | `test_tc04_valid_booking_ahmed`, `test_tc10_book_all_seats_on_route` | PASS |
| **BR-08** | Seats update only after full validation | `book_ticket()` | Deep-copy assertion in `test_tc05`, `test_tc06`, `test_ex01`, `test_ex20` | PASS |
| **BR-09** | Only Confirmed bookings can be cancelled | `cancel_booking()` | `test_tc07_cancel_confirmed_booking`, `test_tc08_reject_repeat_cancellation` | PASS |
| **BR-10** | Restore seats exactly once | `cancel_booking()` | `test_tc07_cancel_confirmed_booking`, `test_tc08_reject_repeat_cancellation` | PASS |
| **BR-11** | Retain cancelled bookings in history | `cancel_booking()`, `show_bookings()` | `test_tc07_cancel_confirmed_booking`, `test_tc11_two_bookings_and_cancel_one` | PASS |
| **BR-12** | Exclude cancelled fares from revenue | `build_report()` | `test_tc11_two_bookings_and_cancel_one`, `test_ex20` | PASS |
| **BR-13** | Capacity invariant: 0 <= avail <= total | `book_ticket()`, `cancel_booking()` | `test_ex20_comprehensive_invariant_reconciliation` | PASS |
| **BR-14** | Menu choices must be supported | `main()`, submenu handlers | `test_tc12_invalid_menu_choices_and_exit`, `test_ex18_invalid_submenu_then_back` | PASS |
| **BR-15** | Valid empty states for all views | `show_bookings()`, `show_routes()`, `build_report()` | `test_tc09_report_on_fresh_state`, `test_ex10_empty_bookings_view`, `test_ex16` | PASS |

---

## 3. Test Scenarios Mapping (TC-01..TC-12 and EX-01..EX-22)

All 34 test cases are tracked and executed in `test_cases.txt` and verified in the automated test suite:
- **TC-01 to TC-12**: Core PRD acceptance scenarios executed and documented.
- **EX-01 to EX-22**: Edge cases, type checks, ID allocations, state isolation, signals, and portability.
- **All 34 test scenarios verified: PASS**.
