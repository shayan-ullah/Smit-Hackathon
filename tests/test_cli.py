"""
CLI and interactive tests for Smart Bus Ticket Booking & Reservation System.
Tests simulated console inputs, error recovery, submenus, EOF/Ctrl+C signals,
process independence, and end-to-end subprocess execution.
Uses standard library unittest and unittest.mock only.
"""

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from main import (
    create_state,
    handle_availability_menu,
    handle_booking,
    handle_cancellation,
    handle_search_route,
    handle_view_routes_menu,
    main,
)


class TestSmartBusCLI(unittest.TestCase):
    """Test suite for CLI interfaces, menu flows, and simulated interactive sessions."""

    def setUp(self):
        self.state = create_state()

    def test_tc12_invalid_menu_choices_and_exit(self):
        """TC-12: Main choice 'abc', '0', '9', then '8' -> helpful errors, repeated menu, clean exit."""
        inputs = ["abc", "0", "9", "8"]
        f = io.StringIO()
        with patch("builtins.input", side_effect=inputs), redirect_stdout(f):
            main()
        output = f.getvalue()

        self.assertIn("Invalid choice. Please select an option from 1 to 8.", output)
        self.assertIn("Thank you for using Smart Bus Reservation System. Goodbye!", output)
        self.assertIn("Notice: In-memory booking records reset upon program termination.", output)

    def test_ex17_eof_and_keyboard_interrupt_handling(self):
        """EX-17: EOFError and KeyboardInterrupt during menu or booking exit gracefully without traceback."""
        # Test EOFError during main menu
        f1 = io.StringIO()
        with patch("builtins.input", side_effect=EOFError), redirect_stdout(f1):
            main()
        out1 = f1.getvalue()
        self.assertIn("Session terminated. Goodbye!", out1)

        # Test KeyboardInterrupt during main menu
        f2 = io.StringIO()
        with patch("builtins.input", side_effect=KeyboardInterrupt), redirect_stdout(f2):
            main()
        out2 = f2.getvalue()
        self.assertIn("Session terminated. Goodbye!", out2)

        # Test EOFError during booking collection -> no booking committed
        state = create_state()
        f3 = io.StringIO()
        with patch("builtins.input", side_effect=["Ahmed", EOFError]), redirect_stdout(f3):
            try:
                handle_booking(state)
            except EOFError:
                pass
        self.assertEqual(len(state["bookings"]), 0)
        self.assertEqual(state["routes"][0]["available_seats"], 40)

    def test_ex18_invalid_submenu_then_back(self):
        """EX-18: Invalid submenu choice in Option 1 and Option 6 shows error, repeats, and returns safely on 0."""
        # Option 1 submenu
        f1 = io.StringIO()
        with patch("builtins.input", side_effect=["99", "0"]), redirect_stdout(f1):
            handle_view_routes_menu(self.state)
        out1 = f1.getvalue()
        self.assertIn("Invalid choice. Please enter 1, 2, 3, or 0.", out1)

        # Option 6 submenu
        f2 = io.StringIO()
        with patch("builtins.input", side_effect=["invalid", "0"]), redirect_stdout(f2):
            handle_availability_menu(self.state)
        out2 = f2.getvalue()
        self.assertIn("Invalid choice. Please enter 1, 2, or 0.", out2)

    def test_ex21_fresh_process_has_independent_state(self):
        """EX-21: Starting a new session begins with initial capacity, empty history, and B1001 candidate."""
        state1 = create_state()
        inputs = ["Ahmed", "24", "R101", "2"]
        with patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()):
            handle_booking(state1)
        self.assertEqual(len(state1["bookings"]), 1)

        # New process simulation
        state2 = create_state()
        self.assertEqual(len(state2["bookings"]), 0)
        self.assertEqual(len(state2["issued_booking_ids"]), 0)
        self.assertEqual(state2["next_booking_number"], 1001)
        self.assertEqual(state2["routes"][0]["available_seats"], 40)

    def test_cli_booking_flow_success_and_failure(self):
        """CLI booking helper handles valid flow, parse errors, and business rule failures."""
        # Successful booking via CLI handler
        f1 = io.StringIO()
        with patch("builtins.input", side_effect=["Bilal", "25", "R101", "2"]), redirect_stdout(f1):
            handle_booking(self.state)
        out1 = f1.getvalue()
        self.assertIn("Booking confirmed!", out1)
        self.assertIn("Booking ID: B1001", out1)
        self.assertIn("Total fare: Rs. 2400", out1)

        # Non-numeric age via CLI handler
        f2 = io.StringIO()
        with patch("builtins.input", side_effect=["Bilal", "invalid_age", "R101", "2"]), redirect_stdout(f2):
            handle_booking(self.state)
        out2 = f2.getvalue()
        self.assertIn("Validation error:", out2)

        # Exceeds seats via CLI handler
        f3 = io.StringIO()
        with patch("builtins.input", side_effect=["Bilal", "25", "R101", "100"]), redirect_stdout(f3):
            handle_booking(self.state)
        out3 = f3.getvalue()
        self.assertIn("Booking failed:", out3)

    def test_cli_cancellation_flow(self):
        """CLI cancellation handles valid cancellation and error conditions."""
        # Prepare a booking
        with patch("builtins.input", side_effect=["Ahmed", "24", "R101", "2"]), redirect_stdout(io.StringIO()):
            handle_booking(self.state)

        # Successful cancellation
        f1 = io.StringIO()
        with patch("builtins.input", return_value="B1001"), redirect_stdout(f1):
            handle_cancellation(self.state)
        out1 = f1.getvalue()
        self.assertIn("Booking B1001 has been cancelled.", out1)
        self.assertIn("Seats restored: 2", out1)
        self.assertIn("Route R101 available seats: 40", out1)

        # Repeat cancellation failure
        f2 = io.StringIO()
        with patch("builtins.input", return_value="B1001"), redirect_stdout(f2):
            handle_cancellation(self.state)
        out2 = f2.getvalue()
        self.assertIn("Cancellation error:", out2)

        # Blank ID cancellation
        f3 = io.StringIO()
        with patch("builtins.input", return_value="   "), redirect_stdout(f3):
            handle_cancellation(self.state)
        out3 = f3.getvalue()
        self.assertIn("Booking ID cannot be blank.", out3)

    def test_cli_search_flow(self):
        """CLI search handles blank input, found matches, and not found."""
        # Blank search query
        f1 = io.StringIO()
        with patch("builtins.input", return_value="   "), redirect_stdout(f1):
            handle_search_route(self.state)
        self.assertIn("Search query cannot be blank.", f1.getvalue())

        # Found match
        f2 = io.StringIO()
        with patch("builtins.input", return_value="Karachi"), redirect_stdout(f2):
            handle_search_route(self.state)
        out2 = f2.getvalue()
        self.assertIn("Search results for 'Karachi':", out2)
        self.assertIn("R101", out2)
        self.assertIn("R102", out2)
        self.assertIn("R104", out2)

        # No match
        f3 = io.StringIO()
        with patch("builtins.input", return_value="NowhereCity"), redirect_stdout(f3):
            handle_search_route(self.state)
        self.assertIn("No routes found matching 'NowhereCity'.", f3.getvalue())

    def test_deterministic_demo_session_mocked(self):
        """Execute the exact 9-step deterministic workflow from 06_ACCEPTANCE_TESTS.md via mocked CLI input."""
        demo_inputs = [
            # 1. View routes (all)
            "1", "1", "0",
            # 2. Book Ahmed, 24, R101, 2
            "3", "Ahmed", "24", "R101", "2",
            # 3. Book Sara, 30, R102, 3
            "3", "Sara", "30", "R102", "3",
            # 4. Cancel B1001
            "5", "B1001",
            # 5. Cancel B1001 again
            "5", "B1001",
            # 6. Report
            "7",
            # 7. View history
            "4",
            # 8. View schedule under option 1
            "1", "3", "0",
            # 9. Exit
            "8",
        ]
        f = io.StringIO()
        with patch("builtins.input", side_effect=demo_inputs), redirect_stdout(f):
            main()
        out = f.getvalue()

        # Check key expectations
        self.assertIn("Booking confirmed!", out)
        self.assertIn("Booking ID: B1001", out)
        self.assertIn("Total fare: Rs. 2400", out)
        self.assertIn("Booking ID: B1002", out)
        self.assertIn("Total fare: Rs. 6000", out)
        self.assertIn("Booking B1001 has been cancelled.", out)
        self.assertIn("Seats restored: 2", out)
        self.assertIn("Cancellation error: Booking B1001 is already cancelled.", out)

        # Check report totals: total=2, conf=1, canc=1, reserved=3, rev=6000, fully_booked=0
        self.assertIn("Total bookings created: 2", out)
        self.assertIn("Confirmed bookings:     1", out)
        self.assertIn("Cancelled bookings:     1", out)
        self.assertIn("Seats currently reserved: 3", out)
        self.assertIn("Confirmed revenue:      Rs. 6000", out)
        self.assertIn("Fully booked routes:    0", out)

    def test_subprocess_execution(self):
        """Execute main.py in a real subprocess using sys.executable to verify end-to-end OS execution."""
        main_path = Path(__file__).resolve().parent.parent / "main.py"
        script_input = "1\n1\n0\n8\n"

        proc = subprocess.run(
            [sys.executable, str(main_path)],
            input=script_input,
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("AVAILABLE BUS ROUTES", proc.stdout)
        self.assertIn("Thank you for using Smart Bus Reservation System. Goodbye!", proc.stdout)


if __name__ == "__main__":
    unittest.main()
