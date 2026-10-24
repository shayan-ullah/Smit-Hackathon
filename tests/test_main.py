"""
Unit tests for Smart Bus Ticket Booking & Reservation System (Core Logic).
Covers business rules, state invariants, data validation, and calculation logic.
Uses Python standard library unittest only.
"""

from contextlib import redirect_stdout
import copy
import io
from pathlib import Path
import sys
import unittest

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from main import (
    SUPPORTED_CITIES,
    book_ticket,
    build_report,
    cancel_booking,
    create_state,
    find_route,
    parse_positive_integer,
    route_status,
    search_routes,
    show_availability,
    show_bookings,
    show_report,
    show_routes,
    show_schedule,
)


class TestSmartBusCore(unittest.TestCase):
    """Test suite covering core logic and acceptance tests."""

    def setUp(self):
        self.state = create_state()

    def test_tc01_initial_routes_and_capacity(self):
        """TC-01: Starter routes R101-R105 correctly configured with total capacity 183."""
        routes = self.state["routes"]
        self.assertEqual(len(routes), 5)
        expected_ids = ["R101", "R102", "R103", "R104", "R105"]
        self.assertEqual([r["route_id"] for r in routes], expected_ids)

        total_cap = sum(r["total_seats"] for r in routes)
        self.assertEqual(total_cap, 183)
        self.assertEqual(sum(r["available_seats"] for r in routes), 183)

        for r in routes:
            self.assertEqual(route_status(r), "Available")
            self.assertEqual(r["available_seats"], r["total_seats"])

    def test_tc02_search_hyderabad(self):
        """TC-02: Search 'hyderabad' returns R101, R103, R105 in order; case & spaces handled."""
        queries = ["hyderabad", "  HYDERABAD  ", "Hyderabad"]
        for q in queries:
            matches = search_routes(self.state, q)
            matched_ids = [r["route_id"] for r in matches]
            self.assertEqual(matched_ids, ["R101", "R103", "R105"])

    def test_tc03_search_unknown_city(self):
        """TC-03: Search 'Atlantis' yields empty results without mutating state."""
        snapshot_before = copy.deepcopy(self.state)
        matches = search_routes(self.state, "Atlantis")
        self.assertEqual(matches, [])
        self.assertEqual(self.state, snapshot_before)

    def test_tc04_valid_booking_ahmed(self):
        """TC-04: Book Ahmed, 24, R101, 2 seats -> B1001, Rs. 2400, R101 avail 38, ID tracked."""
        booking = book_ticket(self.state, "Ahmed", 24, "R101", 2)
        self.assertEqual(booking["booking_id"], "B1001")
        self.assertEqual(booking["passenger_name"], "Ahmed")
        self.assertEqual(booking["passenger_age"], 24)
        self.assertEqual(booking["route_id"], "R101")
        self.assertEqual(booking["seats"], 2)
        self.assertEqual(booking["total_fare"], 2400)
        self.assertEqual(booking["status"], "Confirmed")

        r101 = find_route(self.state, "R101")
        self.assertEqual(r101["available_seats"], 38)
        self.assertIn("B1001", self.state["issued_booking_ids"])
        self.assertEqual(len(self.state["bookings"]), 1)

    def test_tc05_reject_zero_seats(self):
        """TC-05: Attempt booking with 0 seats -> rejected with no state change."""
        snapshot_before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            book_ticket(self.state, "Fatima", 28, "R101", 0)
        self.assertEqual(self.state, snapshot_before)

    def test_tc06_reject_excess_seats(self):
        """TC-06: Attempt booking 41 seats on fresh R101 (capacity 40) -> rejected, no state change."""
        snapshot_before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            book_ticket(self.state, "Zain", 30, "R101", 41)
        self.assertEqual(self.state, snapshot_before)
        r101 = find_route(self.state, "R101")
        self.assertEqual(r101["available_seats"], 40)

    def test_tc07_cancel_confirmed_booking(self):
        """TC-07: Cancel confirmed B1001 -> seats restored to 40, status Cancelled, retained in history."""
        book_ticket(self.state, "Ahmed", 24, "R101", 2)
        cancelled = cancel_booking(self.state, "B1001")
        self.assertEqual(cancelled["status"], "Cancelled")
        self.assertEqual(cancelled["seats"], 2)

        r101 = find_route(self.state, "R101")
        self.assertEqual(r101["available_seats"], 40)
        self.assertIn("B1001", self.state["issued_booking_ids"])
        self.assertEqual(len(self.state["bookings"]), 1)
        self.assertEqual(self.state["bookings"][0]["status"], "Cancelled")

    def test_tc08_reject_repeat_cancellation(self):
        """TC-08: Repeat cancellation of B1001 -> rejected, no extra seats added."""
        book_ticket(self.state, "Ahmed", 24, "R101", 2)
        cancel_booking(self.state, "B1001")

        snapshot_after_first_cancel = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            cancel_booking(self.state, "B1001")
        self.assertEqual(self.state, snapshot_after_first_cancel)
        r101 = find_route(self.state, "R101")
        self.assertEqual(r101["available_seats"], 40)

    def test_tc09_report_on_fresh_state(self):
        """TC-09: Generate report on empty state -> all booking totals and revenue zero."""
        report = build_report(self.state)
        self.assertEqual(report["total_bookings"], 0)
        self.assertEqual(report["confirmed_bookings"], 0)
        self.assertEqual(report["cancelled_bookings"], 0)
        self.assertEqual(report["reserved_seats"], 0)
        self.assertEqual(report["confirmed_revenue"], 0)
        self.assertEqual(report["fully_booked_routes"], 0)

        for summary in report["route_summaries"]:
            self.assertEqual(summary["confirmed_bookings"], 0)
            self.assertEqual(summary["reserved_seats"], 0)
            self.assertEqual(summary["revenue"], 0)

    def test_tc10_book_all_seats_on_route(self):
        """TC-10: Book all 40 seats on R101 -> Rs. 48000, Fully Booked, next request rejected."""
        booking = book_ticket(self.state, "Corporate Group", 35, "R101", 40)
        self.assertEqual(booking["total_fare"], 48000)
        r101 = find_route(self.state, "R101")
        self.assertEqual(r101["available_seats"], 0)
        self.assertEqual(route_status(r101), "Fully Booked")

        # Next request for 1 seat rejected
        snapshot = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            book_ticket(self.state, "Solo", 25, "R101", 1)
        self.assertEqual(self.state, snapshot)

    def test_tc11_two_bookings_and_cancel_one(self):
        """TC-11: Two bookings, cancel one -> report reflects only Confirmed revenue/seats."""
        # Booking 1: Ahmed, R101, 2 seats = Rs. 2400
        book_ticket(self.state, "Ahmed", 24, "R101", 2)
        # Booking 2: Sara, R102, 3 seats = Rs. 6000
        book_ticket(self.state, "Sara", 30, "R102", 3)
        # Cancel B1001
        cancel_booking(self.state, "B1001")

        report = build_report(self.state)
        self.assertEqual(report["total_bookings"], 2)
        self.assertEqual(report["confirmed_bookings"], 1)
        self.assertEqual(report["cancelled_bookings"], 1)
        self.assertEqual(report["reserved_seats"], 3)
        self.assertEqual(report["confirmed_revenue"], 6000)
        self.assertEqual(report["fully_booked_routes"], 0)

        # Per route reconciliation
        r101_summary = next(s for s in report["route_summaries"] if s["route_id"] == "R101")
        r102_summary = next(s for s in report["route_summaries"] if s["route_id"] == "R102")
        self.assertEqual(r101_summary["confirmed_bookings"], 0)
        self.assertEqual(r101_summary["reserved_seats"], 0)
        self.assertEqual(r101_summary["revenue"], 0)
        self.assertEqual(r102_summary["confirmed_bookings"], 1)
        self.assertEqual(r102_summary["reserved_seats"], 3)
        self.assertEqual(r102_summary["revenue"], 6000)

    # ---------------- Extended Tests EX-01 through EX-20 -----------------

    def test_ex01_name_validation(self):
        """EX-01: Reject empty or whitespace-only names; trimmed nonempty name accepted."""
        for invalid_name in ["", "   ", "\t\n"]:
            snapshot = copy.deepcopy(self.state)
            with self.assertRaises(ValueError):
                book_ticket(self.state, invalid_name, 25, "R101", 1)
            self.assertEqual(self.state, snapshot)

        # Nonempty name with outer whitespace gets trimmed
        b = book_ticket(self.state, "  Bilal Khan  ", 25, "R101", 1)
        self.assertEqual(b["passenger_name"], "Bilal Khan")

    def test_ex02_age_validation(self):
        """EX-02: Reject text, 0, negative, decimals, exponents, empty; positive whole age accepted."""
        for invalid_text in ["abc", "0", "-1", "2.5", "1e2", "", "   "]:
            with self.assertRaises(ValueError):
                parse_positive_integer(invalid_text, "Age")

        self.assertEqual(parse_positive_integer("24", "Age"), 24)
        self.assertEqual(parse_positive_integer("+24", "Age"), 24)

    def test_ex03_route_validation(self):
        """EX-03: Reject unknown route R999 or empty route ID with no state change."""
        for invalid_route in ["R999", "", "   ", "UNKNOWN"]:
            snapshot = copy.deepcopy(self.state)
            with self.assertRaises(ValueError):
                book_ticket(self.state, "Tariq", 30, invalid_route, 1)
            self.assertEqual(self.state, snapshot)

    def test_ex04_seat_quantity_validation(self):
        """EX-04: Reject text, -1, 1.5, empty; quantity 1 works."""
        for invalid_seats in ["abc", "-1", "1.5", "", "0"]:
            with self.assertRaises(ValueError):
                parse_positive_integer(invalid_seats, "Seats")

        self.assertEqual(parse_positive_integer("1", "Seats"), 1)

    def test_ex05_case_and_whitespace_id_normalization(self):
        """EX-05: Normalize route and booking IDs with whitespace and mixed case."""
        b = book_ticket(self.state, "Hassan", 22, "  r101  ", 1)
        self.assertEqual(b["route_id"], "R101")
        self.assertEqual(b["booking_id"], "B1001")

        # Cancellation with spaces and lower-case
        cancelled = cancel_booking(self.state, "  b1001  ")
        self.assertEqual(cancelled["status"], "Cancelled")

    def test_ex06_id_sequence_without_reuse(self):
        """EX-06: Three valid bookings with cancellation between get B1001, B1002, B1003 without ID reuse."""
        b1 = book_ticket(self.state, "User1", 20, "R101", 1)
        self.assertEqual(b1["booking_id"], "B1001")
        cancel_booking(self.state, "B1001")

        b2 = book_ticket(self.state, "User2", 21, "R101", 1)
        self.assertEqual(b2["booking_id"], "B1002")

        b3 = book_ticket(self.state, "User3", 22, "R101", 1)
        self.assertEqual(b3["booking_id"], "B1003")

    def test_ex07_collision_avoidance_in_id_allocator(self):
        """EX-07: Pre-populate issued set with B1001; next booking automatically skips to B1002."""
        self.state["issued_booking_ids"].add("B1001")
        b = book_ticket(self.state, "User", 25, "R101", 1)
        self.assertEqual(b["booking_id"], "B1002")

    def test_ex08_cancel_unknown_or_blank_id(self):
        """EX-08: Cancel unknown or blank ID fails with helpful error; state unchanged."""
        snapshot = copy.deepcopy(self.state)
        for invalid_id in ["B9999", "", "   ", "NOTANID"]:
            with self.assertRaises(ValueError):
                cancel_booking(self.state, invalid_id)
            self.assertEqual(self.state, snapshot)

    def test_ex09_state_isolation(self):
        """EX-09: Independent state instances do not share mutable references."""
        state1 = create_state()
        state2 = create_state()

        book_ticket(state1, "User1", 20, "R101", 5)
        self.assertEqual(len(state1["bookings"]), 1)
        self.assertEqual(len(state2["bookings"]), 0)
        self.assertEqual(find_route(state1, "R101")["available_seats"], 35)
        self.assertEqual(find_route(state2, "R101")["available_seats"], 40)

    def test_ex10_empty_bookings_view(self):
        """EX-10: Empty bookings history prints helpful message without exception."""
        f = io.StringIO()
        with redirect_stdout(f):
            show_bookings(self.state)
        output = f.getvalue()
        self.assertIn("No bookings found.", output)

    def test_ex11_route_status_transitions(self):
        """EX-11: Check status transitions: Available -> Partially Booked -> Fully Booked."""
        r105 = find_route(self.state, "R105")
        self.assertEqual(route_status(r105), "Available")

        book_ticket(self.state, "Passenger", 25, "R105", 2)
        self.assertEqual(route_status(r105), "Partially Booked")

        book_ticket(self.state, "Group", 25, "R105", 28)
        self.assertEqual(route_status(r105), "Fully Booked")

    def test_ex12_all_routes_exhausted(self):
        """EX-12: When all routes are fully booked, available-only view reports none available; all view still shows 5."""
        for r in self.state["routes"]:
            book_ticket(self.state, "Bulk", 30, r["route_id"], r["available_seats"])

        # All-routes view still shows all 5
        f1 = io.StringIO()
        with redirect_stdout(f1):
            show_routes(self.state, available_only=False)
        out1 = f1.getvalue()
        for r_id in ["R101", "R102", "R103", "R104", "R105"]:
            self.assertIn(r_id, out1)

        # Available-only view reports helpful empty message
        f2 = io.StringIO()
        with redirect_stdout(f2):
            show_routes(self.state, available_only=True)
        out2 = f2.getvalue()
        self.assertIn("No routes with available seats found.", out2)

    def test_ex13_schedule_structure(self):
        """EX-13: Schedule displays grouped departures and 'No scheduled departures' for Mirpur Khas and Lahore."""
        f = io.StringIO()
        with redirect_stdout(f):
            show_schedule(self.state)
        out = f.getvalue()

        self.assertIn("Karachi", out)
        self.assertIn("Hyderabad", out)
        self.assertIn("Sukkur", out)
        self.assertIn("Mirpur Khas", out)
        self.assertIn("Lahore", out)
        self.assertIn("R101", out)
        self.assertIn("R102", out)
        self.assertIn("R103", out)
        self.assertIn("R104", out)
        self.assertIn("R105", out)
        self.assertEqual(out.count("No scheduled departures."), 2)

    def test_ex14_isolated_report_fixture(self):
        """EX-14: Fresh state except R101 available_seats=0 without bookings -> fully_booked=1, revenue=0."""
        isolated_state = create_state()
        isolated_state["routes"][0]["available_seats"] = 0
        report = build_report(isolated_state)
        self.assertEqual(report["fully_booked_routes"], 1)
        self.assertEqual(report["confirmed_revenue"], 0)
        self.assertEqual(report["reserved_seats"], 0)
        self.assertEqual(report["total_bookings"], 0)

    def test_ex15_search_route_id_and_unknown_id(self):
        """EX-15: Search exact route ID 'R104' returns 1 match; search unknown returns empty."""
        matches = search_routes(self.state, "R104")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["route_id"], "R104")

        matches_unknown = search_routes(self.state, "R999")
        self.assertEqual(matches_unknown, [])

    def test_ex16_empty_routes_fixture(self):
        """EX-16: Empty routes list in state handled gracefully by views and report."""
        empty_state = {"routes": [], "bookings": [], "issued_booking_ids": set(), "next_booking_number": 1001}
        report = build_report(empty_state)
        self.assertEqual(report["fully_booked_routes"], 0)
        self.assertEqual(report["total_bookings"], 0)

        f = io.StringIO()
        with redirect_stdout(f):
            show_routes(empty_state)
            show_availability(empty_state)
        out = f.getvalue()
        self.assertIn("No routes registered.", out)

    def test_ex19_reject_bool_and_non_int_types(self):
        """EX-19: Core book_ticket rejects bool values (True/False) and float types for age and seats."""
        snapshot = copy.deepcopy(self.state)

        # bool for age
        with self.assertRaises(ValueError):
            book_ticket(self.state, "User", True, "R101", 1)  # type: ignore

        # bool for seats
        with self.assertRaises(ValueError):
            book_ticket(self.state, "User", 25, "R101", True)  # type: ignore

        # float for age
        with self.assertRaises(ValueError):
            book_ticket(self.state, "User", 25.5, "R101", 1)  # type: ignore

        # float for seats
        with self.assertRaises(ValueError):
            book_ticket(self.state, "User", 25, "R101", 2.0)  # type: ignore

        self.assertEqual(self.state, snapshot)

    def test_ex20_comprehensive_invariant_reconciliation(self):
        """EX-20: State invariants hold throughout a complex sequence of operations."""
        # Check initial invariants
        self._verify_invariants(self.state)

        # Step 1: Valid booking
        book_ticket(self.state, "A", 20, "R101", 5)
        self._verify_invariants(self.state)

        # Step 2: Invalid booking (over-capacity)
        try:
            book_ticket(self.state, "B", 20, "R101", 100)
        except ValueError:
            pass
        self._verify_invariants(self.state)

        # Step 3: Second valid booking on different route
        book_ticket(self.state, "C", 30, "R103", 4)
        self._verify_invariants(self.state)

        # Step 4: Cancel first booking
        cancel_booking(self.state, "B1001")
        self._verify_invariants(self.state)

        # Step 5: Invalid repeat cancellation
        try:
            cancel_booking(self.state, "B1001")
        except ValueError:
            pass
        self._verify_invariants(self.state)

        # Step 6: Third valid booking
        book_ticket(self.state, "D", 40, "R101", 10)
        self._verify_invariants(self.state)

    def _verify_invariants(self, state):
        """Helper to assert all state invariants described in 04_ARCHITECTURE.md."""
        routes = state["routes"]
        bookings = state["bookings"]
        issued_ids = state["issued_booking_ids"]

        # Route capacities and bounds
        for r in routes:
            self.assertGreater(r["total_seats"], 0)
            self.assertGreaterEqual(r["available_seats"], 0)
            self.assertLessEqual(r["available_seats"], r["total_seats"])

            # total_seats - available_seats == sum(seats for Confirmed bookings on that route)
            confirmed_seats = sum(
                b["seats"] for b in bookings if b["route_id"] == r["route_id"] and b["status"] == "Confirmed"
            )
            self.assertEqual(r["total_seats"] - r["available_seats"], confirmed_seats)

        # Unique booking IDs
        booking_ids = [b["booking_id"] for b in bookings]
        self.assertEqual(len(booking_ids), len(set(booking_ids)))
        for bid in booking_ids:
            self.assertIn(bid, issued_ids)

        # Report reconciliation
        report = build_report(state)
        self.assertEqual(report["total_bookings"], len(bookings))
        self.assertEqual(
            report["confirmed_bookings"], sum(1 for b in bookings if b["status"] == "Confirmed")
        )
        self.assertEqual(
            report["cancelled_bookings"], sum(1 for b in bookings if b["status"] == "Cancelled")
        )
        self.assertEqual(
            report["reserved_seats"], sum(b["seats"] for b in bookings if b["status"] == "Confirmed")
        )
        self.assertEqual(
            report["confirmed_revenue"], sum(b["total_fare"] for b in bookings if b["status"] == "Confirmed")
        )

        sum_route_confirmed = sum(s["confirmed_bookings"] for s in report["route_summaries"])
        sum_route_seats = sum(s["reserved_seats"] for s in report["route_summaries"])
        sum_route_rev = sum(s["revenue"] for s in report["route_summaries"])

        self.assertEqual(report["confirmed_bookings"], sum_route_confirmed)
        self.assertEqual(report["reserved_seats"], sum_route_seats)
        self.assertEqual(report["confirmed_revenue"], sum_route_rev)


if __name__ == "__main__":
    unittest.main()
