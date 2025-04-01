import re
import json
import string

class GICCinemaBooking:
    def __init__(self, config_file=None):
        self.movie_title = ""
        self.rows = 0
        self.seats_per_row = 0
        self.available_seats = {}
        self.bookings = {}
        self.booking_counter = 1
        self.loaded_config = False

        if config_file:
            self.loaded_config = self.load_config(config_file)

    # to prevent re-entering of values when debugging. load configuration from JSON file
    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)

            if isinstance(config, dict):
                # self-initialize
                self.movie_title = config.get("title", self.movie_title)
                self.rows = int(config.get("rows", self.rows))
                self.seats_per_row = int(config.get("seatsPerRow", self.seats_per_row))

                # check if config file dictionary is bogus
                if not self.movie_title or int(self.rows) <= 0 or int(self.seats_per_row) <= 0:
                    return False

                print(f"Loaded configuration: {self.movie_title}, {self.rows}, {self.seats_per_row}")
                return True
        except FileNotFoundError:
            print(f"Config file '{config_file}' not found. Using default values.")
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file '{config_file}'. Using default values.")
        except Exception as e:
            print(f"Error loading config: {e}. Using default values.")
        return False


    def initialize_cinema(self):
        # if there is no config file
        if not self.load_config("theatre_config.json"):
            # allow user to keep trying
            while True:
                try:
                    user_input = input("Please establish the Movie title, Maximum no. of rows (<= 26), Maximum no. of Seats per row (<=50) in the format: [Title] [Row] [SeatsPerRow]\n> ")
                    parts = user_input.split()
                    # check if user enters more parameters or negative numbers
                    pattern = r"^([A-Za-z0-9\s]+)\s+(\d+)\s+(\d+)$"
                    # if this returns False
                    if not re.match(pattern, user_input):
                        raise ValueError("Please input String, +ve integer, +ve integer.")
                    
                    # taking everything except the last 2 objects in the list
                    self.movie_title = " ".join(parts[:-2]) 
                    self.rows = int(parts[-2])
                    self.seats_per_row = int(parts[-1])
                    
                    if not (1 <= self.rows <= 26 and 1 <= self.seats_per_row <= 50):
                        raise ValueError("Rows must be between 1-26 and seats per row between 1-50.")
                    
                    # self storing and initializing the '.' map layout. 'for loop' is to select ABCDEFG... based on the index length of self.rows
                    self.available_seats = {row: ["."] * self.seats_per_row for row in string.ascii_uppercase[:int(self.rows)]}
                    break
                except ValueError as e:
                    print(f"Error: {e}")
        else:
            self.available_seats = {row: ["."] * int(self.seats_per_row) for row in string.ascii_uppercase[:int(self.rows)]}

    # dynamically adjusts SCREEN and dashed lines
    def display_seating(self, booking_id=None):
        total_width = self.seats_per_row * 3  # Each seat takes 3 spaces including padding

        print("\n" + "S C R E E N".center(total_width))
        print("-" * total_width)

        # Get the seats for the given booking ID
        current_booking_seats = set(self.bookings.get(booking_id, [])) if booking_id else set()
        
        # Get all booked seats (from any booking ID)
        all_booked_seats = {seat for seats in self.bookings.values() for seat in seats}

        # Print each row in **reverse order** (so A is at the bottom)
        for row in reversed(string.ascii_uppercase[:self.rows]):
            print(f"{row} ", end="")

            for seat_index, seat in enumerate(self.available_seats[row]):
                if (row, seat_index) in current_booking_seats:
                    print("o ", end=" ")  # 'o' for seats in the given booking_id
                elif (row, seat_index) in all_booked_seats:
                    print("# ", end=" ")  # '#' for other people's booked seats
                else:
                    print(f"{seat:2}", end=" ")  # Available seat

            print()  # Newline after each row

        # Print seat numbers as column headers
        print("  ", end="")
        for seat_num in range(1, self.seats_per_row + 1):
            print(f"{seat_num:2}", end=" ")
        print()

        print("-" * total_width)
        print("Legend: '.' = Available, 'o' = Your Booked Seat, '#' = Occupied\n")

    def display_menu(self):
        while True:
            print(f"\nWelcome to GIC Cinemas")
            available_count = sum(row.count(".") for row in self.available_seats.values())
            print(f"[1] Book tickets for {self.movie_title} ({available_count} seats available)")
            print("[2] Check bookings")
            print("[3] Exit")
            choice = input("Please enter your selection:\n> ")
            if choice == "1":
                # show seats
                self.display_seating()
                self.book_tickets()
            elif choice == "2":
                self.check_bookings()
            elif choice == "3":
                print("Thank you for using GIC Cinemas system. Bye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def book_tickets(self):
        while True:
            num_tickets = input("Enter number of tickets to book, or enter blank to go back to main menu:\n> ")
            if num_tickets == "":
                return
            try:
                num_tickets = int(num_tickets)
                available_count = sum(row.count(".") for row in self.available_seats.values())
                if num_tickets > available_count:
                    print(f"Sorry, there are only {available_count} seats available.\n")
                else:
                    self.assign_seats(num_tickets) # <------
                    return
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    def assign_seats(self, num_tickets):
        users_seats = num_tickets
        selected_seats = []

        for row in self.available_seats.keys():
            if num_tickets == 0:  # Stop if all tickets are assigned
                break

            mid = self.seats_per_row // 2  # Middle index of the row
            row_seats = [i for i, s in enumerate(self.available_seats[row]) if s == "."]

            # Sort available seats by proximity to the middle seat
            row_seats.sort(key=lambda x: abs(x - mid))

            # Determine how many seats we can take from this row
            seats_to_take = min(num_tickets, len(row_seats))

            # Assign seats from this row
            selected_seats.extend((row, seat) for seat in row_seats[:seats_to_take])

            # Reduce the number of tickets left
            num_tickets -= seats_to_take
        
        # region for testing
        # for row, seat in selected_seats:
        #     self.available_seats[row][seat] = "o"
        # self.display_seating()
        # print("")
        # endregion

        booking_id = f"GIC{self.booking_counter:04d}"
        self.booking_counter += 1
        self.bookings[booking_id] = selected_seats
        for row, seat in selected_seats:
            self.available_seats[row][seat] = "o"
        
        print(f"\nSuccessfully reserved {len(selected_seats)} {self.movie_title} tickets.")
        print(f"Booking id: {booking_id}")
        self.display_seating(booking_id)

        # have a confirmation prompt plus have a new seatinng position option.
        # Prompt user to confirm or modify seat selection
        while True:
            # Prompt for seat modification or accept selection
            choice = input("Enter blank to accept seat selection, or enter new seating position\n> ")

            if choice == "":  # If user presses enter without input, confirm booking
                print(f"\nBooking id: {booking_id} confirmed.")
                break  # Exit the loop and confirm the booking

            # Parse the input seat position (e.g., B05)
            row_char = choice[0].upper()  # Row letter (A, B, C, ...)
            seat_num = int(choice[1:]) - 1  # Convert seat number to 0-indexed

            if row_char not in string.ascii_uppercase[:self.rows] or seat_num < 0 or seat_num >= self.seats_per_row:
                print("Invalid seat. Please try again.")
                continue  # Prompt for a valid seat

            # Check if the seat is available for change
            if self.available_seats[row_char][seat_num] != ".":
                print("This seat is already taken. Please select another seat.")
                continue  # Prompt for another seat

            # Remove all previous seat selections by resetting them to available
            for row, seat in self.bookings.get(booking_id, []):  # Get current booked seats for this booking_id
                self.available_seats[row][seat] = "."  # Mark previous booked seats as available
            selected_seats.clear()  # Clear the previous selection

            # Now reassign seats from the new starting position onwards
            new_row_index = string.ascii_uppercase.index(row_char)  # Get the index for the row
            for seat_index in range(seat_num, seat_num + users_seats):  # Assign from the new seat number onwards
                if seat_index >= self.seats_per_row:
                    break  # Stop if we exceed the number of seats in the row

                # If the seat is available, assign it
                if self.available_seats[string.ascii_uppercase[new_row_index]][seat_index] == ".":
                    selected_seats.append((row_char, seat_index))  # Add to the selected seats list
                    self.available_seats[row_char][seat_index] = "o"  # Mark as booked

            # Re-display the updated seating chart
            self.display_seating(booking_id)
    
    def check_bookings(self):
        while True:
            booking_id = input("Enter booking id, or enter blank to go back to main menu:\n> ")
            if booking_id == "":
                return
            if booking_id in self.bookings:
                print(f"\nBooking id: {booking_id}")
                self.display_seating(booking_id)
            else:
                print("Invalid booking id. Please try again.")

if __name__ == "__main__":
    cinema = GICCinemaBooking()
    cinema.initialize_cinema()
    cinema.display_menu()
