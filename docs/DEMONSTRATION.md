# Demonstration Guide & Script

This walkthrough guides an instructor, evaluator, or learner through an interactive 5-to-10 minute demonstration of the Smart Bus Reservation System. It details each command, explains the underlying Python mechanics, and provides model answers for conceptual questions.

---

## 1. Step-by-Step Demonstration Script

### Step 1: Launch Application & Startup Message
- **Action**: Run `python main.py` from the `project/` directory.
- **Console Output**:
  ```text
  Welcome to Smart Bus Ticket Booking & Reservation System!
  (Note: All route and booking data is stored in memory and resets when the program exits.)
  ```
- **Code Explanation**: `create_state()` initializes an isolated dictionary containing the 5 starter routes, an empty booking list, an empty issued ID set, and the booking counter at 1001.

### Step 2: Browse Routes & Initial Capacity
- **Action**: Select `1` (View Available Routes), then `1` (View all routes), then `0` (Back).
- **Observed Behavior**: All 5 routes appear (R101 through R105). Every route displays status `Available`. Total fleet capacity is 183 seats.
- **Code Explanation**: `show_routes(state)` uses `enumerate(routes, start=1)` to print numbered rows. `route_status()` checks `available_seats == total_seats` to return `"Available"`.

### Step 3: Search for a Route (City Search)
- **Action**: Select `2` (Search for a Route), enter `hyderabad`.
- **Observed Behavior**: Routes R101, R103, and R105 are displayed.
- **Code Explanation**: `search_routes(state, query)` uses `.casefold()` comparison against both `departure_city` and `destination_city`. R101 (Karachi -> Hyderabad), R103 (Hyderabad -> Mirpur Khas), and R105 (Sukkur -> Hyderabad) match.

### Step 4: Valid Ticket Booking (Ahmed)
- **Action**: Select `3` (Book a Ticket).
  - Passenger Name: `Ahmed`
  - Passenger Age: `24`
  - Route ID: `R101`
  - Number of seats: `2`
- **Observed Behavior**:
  ```text
  Booking confirmed!
  Booking ID: B1001
  Passenger: Ahmed
  Route: R101 (Karachi -> Hyderabad)
  Seats booked: 2
  Fare per seat: Rs. 1200
  Total fare: Rs. 2400
  Status: Confirmed
  ```
- **Code Explanation**:
  1. `parse_positive_integer()` converts `"24"` and `"2"` to integers.
  2. `book_ticket()` checks availability on R101 (40 >= 2).
  3. Allocates `B1001`, records it in `issued_booking_ids`.
  4. Reduces R101 available seats from 40 to 38.
  5. Computes total fare: `1200 * 2 = 2400`.

### Step 5: Second Valid Booking (Sara)
- **Action**: Select `3` (Book a Ticket).
  - Passenger Name: `Sara`
  - Passenger Age: `30`
  - Route ID: `R102`
  - Number of seats: `3`
- **Observed Behavior**:
  - Assigned ID: `B1002`
  - Total Fare: `Rs. 6000` (`2000 * 3`)
  - Route R102 availability drops from 36 to 33.

### Step 6: Rejected Booking (Validation & Over-Capacity)
- **Action**: Select `3` (Book a Ticket).
  - Attempt seats: `0` -> Rejected: `Validation error: Number of seats must be greater than zero.`
  - Attempt seats on R101: `50` -> Rejected: `Booking failed: Requested 50 seat(s), but only 38 seat(s) are available on route R101.`
- **Code Explanation**: The validate-before-mutate rule ensures that failed validations exit without altering seat counters or generating booking IDs.

### Step 7: Booking Cancellation (Ahmed)
- **Action**: Select `5` (Cancel a Booking), enter `B1001`.
- **Observed Behavior**:
  ```text
  Booking B1001 has been cancelled.
  Seats restored: 2
  Route R101 available seats: 40
  ```
- **Code Explanation**: `cancel_booking()` finds `B1001`, checks `status == "Confirmed"`, updates status to `"Cancelled"`, and adds 2 seats back to R101.

### Step 8: Repeated Cancellation Rejection
- **Action**: Select `5` again, enter `B1001`.
- **Observed Behavior**: `Cancellation error: Booking B1001 is already cancelled.`
- **Code Explanation**: Prevents double-restoration. The seats on R101 remain at 40.

### Step 9: Reconciled Booking Report
- **Action**: Select `7` (Generate Booking Report).
- **Observed Output**:
  ```text
  ========================================
               BOOKING REPORT             
  ========================================
  Total bookings created: 2
  Confirmed bookings:     1
  Cancelled bookings:     1
  Seats currently reserved: 3
  Confirmed revenue:      Rs. 6000
  Fully booked routes:    0
  ----------------------------------------
  Per-Route Breakdown:
    R101 (Karachi -> Hyderabad): 0 confirmed, 0 seat(s), Rs. 0
    R102 (Karachi -> Sukkur): 1 confirmed, 3 seat(s), Rs. 6000
    R103 (Hyderabad -> Mirpur Khas): 0 confirmed, 0 seat(s), Rs. 0
    R104 (Karachi -> Lahore): 0 confirmed, 0 seat(s), Rs. 0
    R105 (Sukkur -> Hyderabad): 0 confirmed, 0 seat(s), Rs. 0
  ========================================
  ```
- **Code Explanation**: Nested loops calculate route-level totals. Sara's booking (`B1002`) provides 1 confirmed booking, 3 reserved seats, and Rs. 6000 revenue. Ahmed's cancelled booking is included in total bookings, but excluded from reserved seats and confirmed revenue.

### Step 10: View My Bookings History
- **Action**: Select `4` (View My Bookings).
- **Observed Behavior**: Displays both records:
  - `B1001 | Ahmed | 24 | R101 | 2 | Rs. 2400 | Cancelled`
  - `B1002 | Sara  | 30 | R102 | 3 | Rs. 6000 | Confirmed`

### Step 11: Route Schedule by Departure City
- **Action**: Select `1` -> `3` (View route schedule by departure city) -> `0` (Back).
- **Observed Behavior**: Displays routes grouped under Karachi, Hyderabad, and Sukkur. Mirpur Khas and Lahore explicitly show `No scheduled departures.`
- **Code Explanation**: Demonstrates nested loops: outer loop iterates through `SUPPORTED_CITIES`, inner loop filters matching routes.

### Step 12: Clean Exit & State Reset
- **Action**: Select `8` (Exit).
- **Observed Behavior**: Program prints goodbye message with in-memory storage reminder and terminates cleanly. Re-launching `python main.py` confirms that booking history is empty and initial seat counts are restored.

---

## 2. Learner Discussion & Evaluation Q&A

**Q1: Why are dictionaries used for routes and bookings instead of parallel lists?**  
*Answer*: Parallel lists (e.g., `route_ids = []`, `prices = []`) require index synchronization, which is fragile and error-prone when records are filtered or sorted. Dictionaries bundle all related attributes into a cohesive record, making the code readable and self-documenting.

**Q2: Why use a set for issued booking IDs instead of checking the bookings list?**  
*Answer*: Checking a list has $O(N)$ linear time complexity. A set offers $O(1)$ constant-time average lookups. More importantly, keeping a dedicated `issued_booking_ids` set guarantees that an ID is never reissued even if a booking is cancelled or removed from active views.

**Q3: How does the application prevent duplicate seat restoration?**  
*Answer*: In `cancel_booking()`, the function checks `target_booking["status"] == "Confirmed"`. Once cancelled, the status is set to `"Cancelled"`. If the user submits the same ID again, the check fails and raises a `ValueError`, ensuring seats are restored exactly once.

**Q4: What is the purpose of for-else in route lookup?**  
*Answer*: A `for-else` block executes its `else` branch only if the loop completes without encountering a `break`. In `find_route()` or `cancel_booking()`, when a match is found, we `break` immediately. If the loop exhausts all elements without breaking, the `else` block executes the not-found logic cleanly without needing temporary boolean flag variables.
