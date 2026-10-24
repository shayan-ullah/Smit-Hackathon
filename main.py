"""
Smart Bus Ticket Booking & Reservation System
A portable, beginner-friendly Python 3 console application.
Manages routes, bookings, cancellations, seat availability, schedules, and reports.
Runtime storage is in-memory and resets on exit.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

# Supported cities stored in an ordered, immutable tuple
SUPPORTED_CITIES: Tuple[str, ...] = (
    "Karachi",
    "Hyderabad",
    "Sukkur",
    "Mirpur Khas",
    "Lahore",
)


def create_state() -> Dict[str, Any]:
    """Create and return a fresh, independent in-memory state dictionary.

    Starter routes are populated with exact PRD baseline fixtures.
    """
    return {
        "routes": [
            {
                "route_id": "R101",
                "departure_city": "Karachi",
                "destination_city": "Hyderabad",
                "departure_time": "08:00 AM",
                "ticket_price": 1200,
                "total_seats": 40,
                "available_seats": 40,
            },
            {
                "route_id": "R102",
                "departure_city": "Karachi",
                "destination_city": "Sukkur",
                "departure_time": "09:30 AM",
                "ticket_price": 2000,
                "total_seats": 36,
                "available_seats": 36,
            },
            {
                "route_id": "R103",
                "departure_city": "Hyderabad",
                "destination_city": "Mirpur Khas",
                "departure_time": "11:00 AM",
                "ticket_price": 800,
                "total_seats": 32,
                "available_seats": 32,
            },
            {
                "route_id": "R104",
                "departure_city": "Karachi",
                "destination_city": "Lahore",
                "departure_time": "07:00 PM",
                "ticket_price": 5000,
                "total_seats": 45,
                "available_seats": 45,
            },
            {
                "route_id": "R105",
                "departure_city": "Sukkur",
                "destination_city": "Hyderabad",
                "departure_time": "02:00 PM",
                "ticket_price": 1500,
                "total_seats": 30,
                "available_seats": 30,
            },
        ],
        "bookings": [],
        "issued_booking_ids": set(),
        "next_booking_number": 1001,
    }


def find_route(state: Dict[str, Any], route_id: str) -> Optional[Dict[str, Any]]:
    """Look up a route by its ID case-insensitively with outer whitespace stripped.

    Demonstrates for-else with break for clean not-found handling.
    """
    if not isinstance(route_id, str):
        return None
    normalized_id = route_id.strip().upper()
    if not normalized_id:
        return None

    for route in state.get("routes", []):
        if route["route_id"].upper() == normalized_id:
            matched_route = route
            break
    else:
        matched_route = None

    return matched_route


def search_routes(state: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """Search for routes by route ID or city (departure/destination).

    Exact route ID check takes precedence and breaks on match.
    City queries return all routes matching either departure or destination city.
    Returns an empty list for empty or non-matching queries without mutating state.
    Demonstrates for-else and break.
    """
    if not isinstance(query, str):
        return []
    clean_query = query.strip()
    if not clean_query:
        return []

    routes = state.get("routes", [])

    # First check for exact route ID match
    for route in routes:
        if route["route_id"].upper() == clean_query.upper():
            return [route]
            break
    else:
        # Otherwise match departure or destination city case-insensitively
        matches = []
        for route in routes:
            if (
                route["departure_city"].casefold() == clean_query.casefold()
                or route["destination_city"].casefold() == clean_query.casefold()
            ):
                matches.append(route)
        return matches


def parse_positive_integer(text: Any, field_label: str = "Value") -> int:
    """Parse a signed base-10 integer string and verify it is > 0.

    Rejects non-strings, decimals, exponents, empty text, zero, and negative values.
    """
    if not isinstance(text, str):
        raise ValueError(f"{field_label} must be a valid text string.")
    cleaned = text.strip()
    if not cleaned:
        raise ValueError(f"{field_label} cannot be blank.")

    # Validate numeric format: optional '+' or '-', followed by one or more digits
    body = cleaned[1:] if cleaned[0] in ("+", "-") else cleaned
    if not body or not body.isdigit():
        raise ValueError(f"{field_label} must be a valid positive whole number.")

    val = int(cleaned)
    if val <= 0:
        raise ValueError(f"{field_label} must be greater than zero.")
    return val


def route_status(route: Dict[str, Any]) -> str:
    """Classify route status based on available vs total seats.

    Available: all seats remain.
    Partially Booked: 0 < available < total.
    Fully Booked: 0 seats remain.
    """
    available = route.get("available_seats", 0)
    total = route.get("total_seats", 0)

    if available == total:
        return "Available"
    elif available == 0:
        return "Fully Booked"
    elif 0 < available < total:
        return "Partially Booked"
    else:
        return "Unknown"


def book_ticket(
    state: Dict[str, Any],
    name: str,
    age: int,
    route_id: str,
    seats: int,
) -> Dict[str, Any]:
    """Validate all booking inputs and commit a new booking if valid.

    Strict validate-before-mutate policy: if any validation fails,
    state (routes, bookings, issued IDs, next number) is left completely unchanged.
    """
    # 1. Passenger Name validation (BR-01, EX-01)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Passenger name cannot be blank.")
    clean_name = name.strip()

    # 2. Passenger Age validation (BR-02, EX-02, EX-19)
    # Reject booleans (isinstance(True, int) is True in Python) and non-integers
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("Passenger age must be an integer.")
    if age <= 0:
        raise ValueError("Passenger age must be a positive integer greater than zero.")

    # 3. Route ID validation (BR-03, EX-03)
    if not isinstance(route_id, str) or not route_id.strip():
        raise ValueError("Route ID cannot be blank.")
    clean_route_id = route_id.strip().upper()
    route = find_route(state, clean_route_id)
    if route is None:
        raise ValueError(f"Route '{clean_route_id}' does not exist.")

    # 4. Seat Quantity validation (BR-04, EX-04, EX-19)
    if isinstance(seats, bool) or not isinstance(seats, int):
        raise ValueError("Number of seats must be an integer.")
    if seats <= 0:
        raise ValueError("Number of seats must be a positive integer greater than zero.")

    # 5. Availability check (BR-05, BR-13, TC-06, TC-10)
    if seats > route["available_seats"]:
        raise ValueError(
            f"Requested {seats} seat(s), but only {route['available_seats']} seat(s) are available on route {clean_route_id}."
        )

    # 6. Allocate Unique Booking ID (BR-06, EX-06, EX-07)
    candidate_num = state["next_booking_number"]
    while f"B{candidate_num}" in state["issued_booking_ids"]:
        candidate_num += 1
    booking_id = f"B{candidate_num}"

    # 7. Fare calculation (BR-07, RQ-08)
    ticket_price = route["ticket_price"]
    total_fare = ticket_price * seats

    # 8. Commit state changes atomically
    state["next_booking_number"] = candidate_num + 1
    state["issued_booking_ids"].add(booking_id)
    route["available_seats"] -= seats

    booking_record: Dict[str, Any] = {
        "booking_id": booking_id,
        "passenger_name": clean_name,
        "passenger_age": age,
        "route_id": route["route_id"],
        "seats": seats,
        "total_fare": total_fare,
        "status": "Confirmed",
    }
    state["bookings"].append(booking_record)

    return booking_record


def cancel_booking(state: Dict[str, Any], booking_id: str) -> Dict[str, Any]:
    """Cancel an existing Confirmed booking by ID, restoring seats to the route once.

    Retains the original booking record with status 'Cancelled'.
    Rejects unknown or already cancelled IDs without mutating state.
    Demonstrates for-else with break.
    """
    if not isinstance(booking_id, str) or not booking_id.strip():
        raise ValueError("Booking ID cannot be blank.")
    clean_id = booking_id.strip().upper()

    # Locate booking using for-else and break
    target_booking = None
    for b in state.get("bookings", []):
        if b["booking_id"].upper() == clean_id:
            target_booking = b
            break
    else:
        raise ValueError(f"Booking ID '{clean_id}' not found.")

    # Only Confirmed bookings can be cancelled (BR-09, BR-10)
    if target_booking["status"] != "Confirmed":
        raise ValueError(f"Booking {clean_id} is already cancelled.")

    # Find the associated route to restore seats
    route = find_route(state, target_booking["route_id"])
    if route is None:
        raise ValueError(f"Route '{target_booking['route_id']}' associated with booking {clean_id} not found.")

    # Atomic cancellation commit: restore seats and update status
    route["available_seats"] += target_booking["seats"]
    target_booking["status"] = "Cancelled"

    return target_booking


def build_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate booking metrics and per-route breakdowns without mutating state.

    Uses nested loops (outer routes, inner bookings) to aggregate confirmed
    bookings, seats, and revenue per route.
    """
    bookings = state.get("bookings", [])
    routes = state.get("routes", [])

    total_bookings = len(bookings)
    confirmed_bookings = 0
    cancelled_bookings = 0
    reserved_seats = 0
    confirmed_revenue = 0

    for b in bookings:
        if b["status"] == "Confirmed":
            confirmed_bookings += 1
            reserved_seats += b["seats"]
            confirmed_revenue += b["total_fare"]
        elif b["status"] == "Cancelled":
            cancelled_bookings += 1

    fully_booked_routes = 0
    for r in routes:
        if r["available_seats"] == 0:
            fully_booked_routes += 1

    # Nested loops: outer loop routes, inner loop bookings
    route_summaries = []
    for r in routes:
        r_conf_count = 0
        r_reserved_seats = 0
        r_revenue = 0
        for b in bookings:
            if b["route_id"] == r["route_id"] and b["status"] == "Confirmed":
                r_conf_count += 1
                r_reserved_seats += b["seats"]
                r_revenue += b["total_fare"]
        route_summaries.append(
            {
                "route_id": r["route_id"],
                "departure_city": r["departure_city"],
                "destination_city": r["destination_city"],
                "confirmed_bookings": r_conf_count,
                "reserved_seats": r_reserved_seats,
                "revenue": r_revenue,
            }
        )

    return {
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "reserved_seats": reserved_seats,
        "confirmed_revenue": confirmed_revenue,
        "fully_booked_routes": fully_booked_routes,
        "route_summaries": route_summaries,
    }


# =====================================================================
# Console Views and Display Helpers
# =====================================================================


def show_routes(state: Dict[str, Any], available_only: bool = False) -> None:
    """Display bus routes in a formatted table.

    Demonstrates enumerate() and continue to skip fully booked routes when filtered.
    """
    routes = state.get("routes", [])
    if not routes:
        print("\nNo routes registered.")
        return

    title = "AVAILABLE BUS ROUTES (SEATS REMAINING)" if available_only else "AVAILABLE BUS ROUTES"
    print(f"\n{title}")
    header = f"{'No.':<4}{'Route':<7}{'Journey':<32}{'Depart':<11}{'Fare':<11}{'Seats':<10}{'Status'}"
    print(header)
    print("-" * len(header))

    displayed_count = 0
    for idx, route in enumerate(routes, start=1):
        # Demonstrate continue to skip fully booked routes if filtered
        if available_only and route["available_seats"] == 0:
            continue

        status = route_status(route)
        journey = f"{route['departure_city']} -> {route['destination_city']}"
        fare_str = f"Rs. {route['ticket_price']}"
        seats_str = f"{route['available_seats']}/{route['total_seats']}"

        print(
            f"{idx:<4}{route['route_id']:<7}{journey:<32}{route['departure_time']:<11}{fare_str:<11}{seats_str:<10}{status}"
        )
        displayed_count += 1

    if displayed_count == 0:
        print("No routes with available seats found.")


def show_availability(state: Dict[str, Any], available_only: bool = False) -> None:
    """Display seat availability overview with Available, Partially Booked, or Fully Booked status.

    Demonstrates enumerate() and continue.
    """
    routes = state.get("routes", [])
    if not routes:
        print("\nNo routes registered.")
        return

    title = "SEAT AVAILABILITY (AVAILABLE ONLY)" if available_only else "SEAT AVAILABILITY"
    print(f"\n{title}")
    header = f"{'No.':<4}{'Route':<7}{'Journey':<32}{'Available':<11}{'Total':<8}{'Status'}"
    print(header)
    print("-" * len(header))

    displayed_count = 0
    for idx, route in enumerate(routes, start=1):
        if available_only and route["available_seats"] == 0:
            continue

        status = route_status(route)
        journey = f"{route['departure_city']} -> {route['destination_city']}"
        print(
            f"{idx:<4}{route['route_id']:<7}{journey:<32}{route['available_seats']:<11}{route['total_seats']:<8}{status}"
        )
        displayed_count += 1

    if displayed_count == 0:
        print("No routes with available seats found.")


def show_schedule(state: Dict[str, Any]) -> None:
    """Display route schedules grouped by departure city.

    Demonstrates nested loops (outer SUPPORTED_CITIES, inner routes)
    and reports 'No scheduled departures.' for cities with no departing routes.
    """
    print("\nROUTE SCHEDULE BY DEPARTURE CITY")
    routes = state.get("routes", [])

    for city in SUPPORTED_CITIES:
        print(city)
        departures = []
        for route in routes:
            if route["departure_city"].casefold() == city.casefold():
                departures.append(route)

        if departures:
            for r in departures:
                print(f"  {r['route_id']} -> {r['destination_city']:<14} | {r['departure_time']}")
        else:
            print("  No scheduled departures.")


def show_bookings(state: Dict[str, Any]) -> None:
    """List all booking records created in this session, including cancelled ones.

    Demonstrates enumerate(). Shows 'No bookings found.' when list is empty.
    """
    bookings = state.get("bookings", [])
    if not bookings:
        print("\nNo bookings found.")
        return

    print("\nMY BOOKINGS")
    header = f"{'No.':<4}{'Booking ID':<12}{'Passenger':<18}{'Age':<6}{'Route':<8}{'Seats':<7}{'Total Fare':<13}{'Status'}"
    print(header)
    print("-" * len(header))

    for idx, b in enumerate(bookings, start=1):
        fare_str = f"Rs. {b['total_fare']}"
        print(
            f"{idx:<4}{b['booking_id']:<12}{b['passenger_name']:<18}{b['passenger_age']:<6}{b['route_id']:<8}{b['seats']:<7}{fare_str:<13}{b['status']}"
        )


def show_report(state: Dict[str, Any]) -> None:
    """Display comprehensive booking report and reconciled per-route summary."""
    report = build_report(state)

    print("\n========================================")
    print("             BOOKING REPORT             ")
    print("========================================")
    print(f"Total bookings created: {report['total_bookings']}")
    print(f"Confirmed bookings:     {report['confirmed_bookings']}")
    print(f"Cancelled bookings:     {report['cancelled_bookings']}")
    print(f"Seats currently reserved: {report['reserved_seats']}")
    print(f"Confirmed revenue:      Rs. {report['confirmed_revenue']}")
    print(f"Fully booked routes:    {report['fully_booked_routes']}")
    print("----------------------------------------")
    print("Per-Route Breakdown:")
    for summary in report["route_summaries"]:
        journey = f"{summary['departure_city']} -> {summary['destination_city']}"
        print(
            f"  {summary['route_id']} ({journey}): {summary['confirmed_bookings']} confirmed, {summary['reserved_seats']} seat(s), Rs. {summary['revenue']}"
        )
    print("========================================")


# =====================================================================
# Submenu Handlers and Booking Collection
# =====================================================================


def handle_view_routes_menu(state: Dict[str, Any]) -> None:
    """Handle Option 1 submenu navigation for browsing routes and schedules."""
    while True:
        print("\n--- View Routes ---")
        print("1. View all routes")
        print("2. View routes with available seats only")
        print("3. View route schedule by departure city")
        print("0. Back to main menu")
        sub_choice = input("Enter choice: ").strip()

        if sub_choice == "1":
            show_routes(state, available_only=False)
        elif sub_choice == "2":
            show_routes(state, available_only=True)
        elif sub_choice == "3":
            show_schedule(state)
        elif sub_choice == "0":
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 0.")
            continue


def handle_search_route(state: Dict[str, Any]) -> None:
    """Handle Option 2: Search for routes by route ID or city name."""
    query = input("\nEnter route ID or city: ").strip()
    if not query:
        print("Search query cannot be blank.")
        return

    results = search_routes(state, query)
    if results:
        print(f"\nSearch results for '{query}':")
        for r in results:
            journey = f"{r['departure_city']} -> {r['destination_city']}"
            print(f"{r['route_id']} | {journey} | Rs. {r['ticket_price']} | {r['available_seats']} seats available")
    else:
        print(f"No routes found matching '{query}'.")


def handle_booking(state: Dict[str, Any]) -> None:
    """Handle Option 3: Collect inputs, validate, and book a ticket."""
    print("\n--- Book a Ticket ---")
    name = input("Enter passenger name: ")
    age_raw = input("Enter passenger age: ")
    route_id = input("Enter route ID: ")
    seats_raw = input("Enter number of seats to book: ")

    # Parse and validate numeric fields
    try:
        age = parse_positive_integer(age_raw, "Passenger age")
        seats = parse_positive_integer(seats_raw, "Number of seats")
    except ValueError as err:
        print(f"Validation error: {err}")
        return

    # Call business logic
    try:
        booking = book_ticket(state, name, age, route_id, seats)
    except ValueError as err:
        print(f"Booking failed: {err}")
        return

    # Display confirmation matching PRD sample format
    route = find_route(state, booking["route_id"])
    journey = f"{route['departure_city']} -> {route['destination_city']}" if route else booking["route_id"]
    unit_fare = route["ticket_price"] if route else booking["total_fare"] // booking["seats"]

    print("\nBooking confirmed!")
    print(f"Booking ID: {booking['booking_id']}")
    print(f"Passenger: {booking['passenger_name']}")
    print(f"Route: {booking['route_id']} ({journey})")
    print(f"Seats booked: {booking['seats']}")
    print(f"Fare per seat: Rs. {unit_fare}")
    print(f"Total fare: Rs. {booking['total_fare']}")
    print(f"Status: {booking['status']}")


def handle_cancellation(state: Dict[str, Any]) -> None:
    """Handle Option 5: Cancel a booking by ID."""
    booking_id = input("\nEnter booking ID to cancel: ").strip()
    if not booking_id:
        print("Cancellation error: Booking ID cannot be blank.")
        return

    try:
        cancelled_b = cancel_booking(state, booking_id)
    except ValueError as err:
        print(f"Cancellation error: {err}")
        return

    route = find_route(state, cancelled_b["route_id"])
    remaining_avail = route["available_seats"] if route else "unknown"

    print(f"\nBooking {cancelled_b['booking_id']} has been cancelled.")
    print(f"Seats restored: {cancelled_b['seats']}")
    print(f"Route {cancelled_b['route_id']} available seats: {remaining_avail}")


def handle_availability_menu(state: Dict[str, Any]) -> None:
    """Handle Option 6 submenu navigation for seat availability."""
    while True:
        print("\n--- Seat Availability ---")
        print("1. View all routes")
        print("2. View routes with available seats only")
        print("0. Back to main menu")
        sub_choice = input("Enter choice: ").strip()

        if sub_choice == "1":
            show_availability(state, available_only=False)
        elif sub_choice == "2":
            show_availability(state, available_only=True)
        elif sub_choice == "0":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 0.")
            continue


# =====================================================================
# Main Application Loop
# =====================================================================


def main() -> None:
    """Main program entry point with persistent session state and continuous loop."""
    print("Welcome to Smart Bus Ticket Booking & Reservation System!")
    print("(Note: All route and booking data is stored in memory and resets when the program exits.)")

    state = create_state()

    try:
        while True:
            print("\n================================")
            print("  SMART BUS RESERVATION SYSTEM  ")
            print("================================")
            print("1. View Available Routes")
            print("2. Search for a Route")
            print("3. Book a Ticket")
            print("4. View My Bookings")
            print("5. Cancel a Booking")
            print("6. View Seat Availability")
            print("7. Generate Booking Report")
            print("8. Exit")
            print("================================")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                handle_view_routes_menu(state)
            elif choice == "2":
                handle_search_route(state)
            elif choice == "3":
                handle_booking(state)
            elif choice == "4":
                show_bookings(state)
            elif choice == "5":
                handle_cancellation(state)
            elif choice == "6":
                handle_availability_menu(state)
            elif choice == "7":
                show_report(state)
            elif choice == "8":
                print("\nThank you for using Smart Bus Reservation System. Goodbye!")
                print("Notice: In-memory booking records reset upon program termination.")
                break
            else:
                print("Invalid choice. Please select an option from 1 to 8.")
                continue

    except (KeyboardInterrupt, EOFError):
        print("\n\nSession terminated. Goodbye! (In-memory booking records have reset.)")


if __name__ == "__main__":
    main()
