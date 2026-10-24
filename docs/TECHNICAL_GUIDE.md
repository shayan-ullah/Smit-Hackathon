# Technical Architecture & Beginner Concepts Guide

## 1. System Overview & Architecture

The Smart Bus Reservation System is a modular console application written in Python 3. It models real-world transportation management—route lookups, ticket reservation, seat inventory control, cancellations, schedules, and financial reports—using fundamental Python data structures and algorithms without external frameworks or databases.

### Module Layout
All business logic, state factories, validation routines, formatting helpers, and the interactive command-line loop reside in `main.py`. Test suites and documentation import `main.py` directly without initiating interactive console prompts due to standard `if __name__ == '__main__': main()` shielding.

---

## 2. In-Memory State Model & Data Structures

The system maintains process-level state encapsulated within a single dictionary returned by `create_state()`. Every function takes `state` as an explicit parameter, ensuring state isolation and testability.

```python
state = {
    "routes": [ ... ],             # List of dictionaries (ordered route inventory)
    "bookings": [ ... ],           # List of dictionaries (chronological booking history)
    "issued_booking_ids": set(),   # Set of strings (O(1) uniqueness check)
    "next_booking_number": 1001    # Integer counter for monotonic ID generation
}
```

### Why These Data Structures Were Chosen

1. **List (`routes`, `bookings`)**:
   - `routes` represents an ordered collection of fixed routes. A list preserves insertion order, allows indexing with `enumerate()`, and provides straightforward sequential traversal.
   - `bookings` retains every booking record in chronological order, allowing users to view full reservation history.

2. **Dictionary (`route`, `booking`)**:
   - Models entities with named attributes (`route_id`, `departure_city`, `ticket_price`, `available_seats`, etc.).
   - Provides clear, self-documenting key access (e.g., `booking["total_fare"]`) without complex class boilerplate.

3. **Tuple (`SUPPORTED_CITIES`)**:
   - An immutable ordered sequence `("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")`.
   - Represents the fixed geographical scope of the transit network. Immortality guarantees that supported cities cannot be accidentally modified, deleted, or reordered at runtime.

4. **Set (`issued_booking_ids`)**:
   - Tracks every booking ID issued during the program lifecycle (e.g., `{"B1001", "B1002"}`).
   - Provides $O(1)$ constant-time lookup to enforce globally unique booking IDs and prevent ID recycling even after cancellation.

5. **Integer Currency (`ticket_price`, `total_fare`, `confirmed_revenue`)**:
   - All monetary values are represented in integer Pakistani Rupees (`Rs.`).
   - Floating-point representations (`float`) introduce rounding anomalies (e.g., `0.1 + 0.2 != 0.3`) in financial calculations. Since bus fares in this domain are whole rupee amounts, integers provide exact arithmetic without fractional drift.

---

## 3. Core Business Logic & State Invariants

### 3.1 Validate-Before-Mutate Contract
The application enforces strict validation before altering any runtime state:
- When booking a ticket (`book_ticket`), passenger name, age, route ID, and seat counts are validated in memory.
- If any check fails, a `ValueError` is raised immediately.
- The `routes` availability, `bookings` list, `issued_booking_ids` set, and `next_booking_number` counter remain untouched. Automated tests verify this by asserting deep-copy equality of the state before and after invalid calls.

### 3.2 Monotonic ID Allocation & Collision Prevention
- Candidate IDs begin with `f"B{state['next_booking_number']}"`.
- Before assigning an ID, the allocator inspects `state["issued_booking_ids"]`. If an ID is present, it increments the local candidate counter until an unissued ID is located.
- On successful commit, the ID is added to the set and the state counter is updated.

### 3.3 One-Time Seat Restoration & Retained History
- When a booking is cancelled (`cancel_booking`), the system verifies that the record exists and has status `Confirmed`.
- The booking's status changes to `Cancelled`, and its seat quantity is restored to the associated route.
- The cancelled booking remains in `state["bookings"]` for history and audit tracking.
- Subsequent cancellation requests for the same ID are rejected because the status is no longer `Confirmed`, preventing double-restoration defects.

### 3.4 Report Reconciliation Arithmetic
- **Total Bookings**: Count of all records in `state["bookings"]` (Confirmed + Cancelled).
- **Confirmed Bookings**: Count of bookings with status `Confirmed`.
- **Cancelled Bookings**: Count of bookings with status `Cancelled`.
- **Reserved Seats**: Sum of seats for `Confirmed` bookings only.
- **Confirmed Revenue**: Sum of `total_fare` for `Confirmed` bookings only.
- **Fully Booked Routes**: Count of routes where `available_seats == 0`.
- **Per-Route Aggregation**: Uses an outer loop over `routes` and an inner loop over `bookings` to accumulate route-specific confirmed seats and revenue. The sum of per-route figures matches aggregate totals exactly.

---

## 4. Required Python Concepts Traceability Table

The table below documents how each required Python language construct from PRD Section 11 is meaningfully utilized in `main.py`:

| Python Concept | Verified Implementation in `main.py` | Plain Explanation & Purpose |
| --- | --- | --- |
| `print()` & `input()` | `main()`, `handle_booking()`, `show_routes()` | Displays interactive menus, formatted tables, and confirmation banners; reads user inputs. |
| Variables & Basic Types | `state`, `clean_name`, `age`, `route_id`, `seats` | Holds passenger inputs, counters, fares, and system configuration data in local and state variables. |
| Strings (`str`) | `b["booking_id"]`, `b["status"]` | Manages text fields such as passenger names, route IDs, cities, statuses, and times. |
| Integers (`int`) | `age`, `seats`, `ticket_price`, `total_fare` | Represents numeric quantities such as passenger age, seat counts, and exact rupee currency. |
| Booleans (`bool`) | `available_only`, `isinstance(age, bool)` | Controls conditional view filtering and guards against treating boolean values as integers. |
| Lists (`list`) | `state["routes"]`, `state["bookings"]` | Ordered collections storing route definitions and chronological booking histories. |
| Dictionaries (`dict`) | `route`, `booking_record`, `state` | Key-value records grouping related attributes for individual routes and bookings. |
| Tuples (`tuple`) | `SUPPORTED_CITIES` | Immutable sequence defining the fixed network of transit cities in canonical order. |
| Sets (`set`) | `state["issued_booking_ids"]` | Unordered hash set tracking issued booking IDs for fast $O(1)$ duplicate prevention. |
| `if`, `elif`, `else` | `main()` menu dispatch, `route_status()` | Directs control flow based on user menu selections and seat availability thresholds. |
| Nested conditions | `book_ticket()`, `handle_view_routes_menu()` | Hierarchically checks type, range, route existence, and capacity before mutating state. |
| `for` loops | `show_bookings()`, `search_routes()` | Iterates through collections of routes, bookings, and search matches. |
| Nested `for` loops | `build_report()`, `show_schedule()` | Routes-outer / bookings-inner to aggregate route revenue; cities-outer / routes-inner for schedules. |
| `for-else` with `break` | `find_route()`, `cancel_booking()`, `search_routes()` | Breaks early when a matching route or booking is found; `else` block executes clean not-found logic. |
| `continue` | `show_routes()`, `show_availability()` | Skips fully booked routes when the user requests an available-only filtered view. |
| `enumerate()` | `show_routes()`, `show_bookings()` | Generates 1-indexed display sequence numbers for formatted console tables. |
| `while` loops | `main()`, `handle_view_routes_menu()` | Maintains continuous console session loops until explicit user termination. |
| Arithmetic expressions | `ticket_price * seats`, `total_seats - seats` | Calculates total fares, decrements/restores seat availability, and sums report totals. |
| Input validation | `parse_positive_integer()`, `book_ticket()` | Validates user strings, rejects negative/zero/malformed data, and prevents runtime crashes. |
| Exception handling | `try-except (ValueError, EOFError, KeyboardInterrupt)` | Catches conversion errors gracefully and allows clean program exit without Python tracebacks. |
