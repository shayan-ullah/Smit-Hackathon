# Evidence Index: Smart Bus Reservation System

This directory contains genuine execution evidence and visual captures gathered during automated verification and deterministic console execution.

## Image Captures

All four images in this directory are labeled:
`Rendered capture of actual program stdout`

They were generated using native Windows .NET `System.Drawing` from the unaltered stdout stream produced during the deterministic demonstration session, formatted in a clean monospace terminal console view with dark background (`#1e1e1e`) and ClearType text rendering. No image packages or runtime dependencies were added to the application itself.

| Image File | Content Description | Observed Session Data |
| --- | --- | --- |
| `routes.png` | View Available Routes (Option 1 -> 1) | Shows initial routes R101–R105, departure times, fares in integer rupees, initial 183/183 available seats, all status `Available`. |
| `booking.png` | Valid Booking Confirmation (Option 3) | Shows booking confirmation for Ahmed (age 24, route R101, 2 seats), assigned ID `B1001`, fare per seat Rs. 1200, total fare Rs. 2400, status `Confirmed`. |
| `cancellation.png` | Cancellation & Repeat Attempt (Option 5) | Shows cancellation of `B1001` restoring 2 seats to R101 (availability back to 40), followed immediately by rejected duplicate cancellation error without extra restoration. |
| `report.png` | Booking Report & Reconciliation (Option 7) | Shows reconciled report: Total bookings: 2, Confirmed: 1, Cancelled: 1, Seats reserved: 3, Confirmed revenue: Rs. 6000, Fully booked routes: 0, plus per-route summary. |

## Text Evidence Files

- `commands.md`: Exact commands executed, working directories, return codes, and test run summaries.
- `unit-tests.txt`: Full console output from `python -m unittest tests/test_main.py -v` (core domain, validation, and state invariant checks).
- `cli-tests.txt`: Full console output from `python -m unittest tests/test_cli.py -v` (interactive navigation, submenus, EOF/Ctrl+C signals, and subprocess runs).
- `demo-session.txt`: Complete, unaltered transcript of the 9-step deterministic console session executed through `main.py`.

## Verification Policy
No results or image artifacts are fabricated. All values correspond exactly to actual program execution against the initial PRD baseline fixtures.
