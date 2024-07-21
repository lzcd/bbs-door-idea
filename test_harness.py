import sys
import os
import unittest
from typing import Self

sys.path.append(os.path.relpath('doors'))

from doors import door
from doors import franks_doors


class TicTacToeTests(unittest.TestCase):
    
    def test_can_play_game(self):

        # This part of the test is from the perspective of BBS1.
        # The user has selected the Tic Tac Toe door.
        # How you choose to remember what door is currently active for a given user is up to you.
        # For the sake of this demo / unit test, we're going to hardcode / assume what door is currently active.



        # The door host is how the door communicates back to the BBS.
        # For the sake of this test, we have a mock door host that only does enough to support the demo / unit test.
        # For the real BBS code, you'd wire up a host to actually do stuff properly like store stuff in a DB, communicate with remotes BBSes etc.
        host = MockDoorHost()

        # Jane is our local user. Bob is our remote user.
        # Frank provded a collection of doors. We are only focusing on the tic tac toe door for this test.

        # We pass in no command initially so that the door (re)prints the menu options.
        franks_doors.tic_tac_toe.try_process_local_command(host, "jane", None)

        # Our mock door host recorded what the door wanted to display to Jane.
        # For the reall BBS, the host wuld receive a call to print_local function.
        self.assertEqual(host.local_output, "[C]reate new game\ne[X]it")
        # Behind the scenes it also attempted to load the door state for Jane, update it and then store it.
        # For the real host, you'd probably wire up these calls to load and store to a DB table with the sender "Jane" as one of the keys.
        # The door is responsible for the state and the host doesn't need to know anything about it beyond to store and load it as requested.

        # Jane types "c" to create a new game
        franks_doors.tic_tac_toe.try_process_local_command(host, "jane", "c")
        # And the game asks for the opponents name
        self.assertEqual(host.local_output, "Opponent's short name?\ne[X]it")

        # Jane wants to play against Bob
        franks_doors.tic_tac_toe.try_process_local_command(host, "jane", "bob")
        # Note: There's probably some validation of the opponents short name that needs to happen at this point but I didn't want to complicate this example.
        # I'm imagining the validation would probably take the form a new host function. e.g. host.validate_short_name(short_name : str) -> bool

        # Anyway...
        # Jane gets presented with the current state of the game board and asked to pick a move
        self.assertEqual(host.local_output, "0 | 1 | 2\n---------\n3 | 4 | 5\n---------\n6 | 7 | 8\n\nWhere do you want to place your piece?\n(0, 1, 2, 3, 4, 5, 6, 7, 8)\ne[X]it")
        # jane picks the obvious spot
        franks_doors.tic_tac_toe.try_process_local_command(host, "jane", "4")
        # behind the scenes a message is sent to Bob
        self.assertEqual(host.remote_recipient, "bob")
        self.assertEqual(host.remote_command, "    X    ")
        
        # When the message shows up at the remote location, BB@ would make a call like the following to its door
        franks_doors.tic_tac_toe.try_process_local_command(host, "bob", "    X    ")




class MockDoorHost(door.DoorHost):
    def __init__(self: Self) -> None:
        super().__init__()
        self.state = None
        self.local_output = None
        self.remote_recipient = None
        self.remote_command = None
        self.door_exit_requestd = False

    def load_state(self: Self, short_name: str) -> str:
        return self.state

    def store_state(self: Self, short_name: str, state: str) -> None:
        self.state = state
    
    def print_local(self: Self, sender_short_name : str, data: str) -> None:
        self.local_output = data

    def send_remote_command(self: Self, sender_short_name: str, recipient_short_name : str, data: str) -> None:
        self.remote_recipient = recipient_short_name
        self.remote_command = data

    def exit_door(self: Self, short_name: str) -> None:
        self.door_exit_requestd = True
        
if __name__ == '__main__':
    unittest.main()