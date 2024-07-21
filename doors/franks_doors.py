from enum import Enum, IntEnum, StrEnum, auto
from door import DoorHost, Door

import json

class TttState(StrEnum):
    CurrentScreen = auto()
    GamesByOpponentName = auto()
    CurrentOpponentName = auto()
    Board = auto()
    CurrenTurnPlayer = auto()
    PlayerPiece = auto()

class TttBoardSquareState(IntEnum):
    Empty = auto()
    PlayerOne = auto()
    PlayerTwo = auto()

class TttScreen(StrEnum):
    Main = auto()
    OpponentName = auto()
    Game = auto()

class tic_tac_toe(Door):
    def try_process_local_command(host: DoorHost, sender_short_name : str, data: str) -> bool:
        output_lines = []

        # load current state
        serialised_state = host.load_state(sender_short_name)
        if serialised_state == None:
            state = {}
            state[TttState.CurrentScreen] = TttScreen.Main
            state[TttState.GamesByOpponentName] = {}
            state[TttState.CurrentOpponentName] = 0
        else:
            state = json.loads(serialised_state)

        # perform requested action
        match state[TttState.CurrentScreen]:
            case TttScreen.Main:
                match data:
                    case None:
                        pass
                    case "c":
                        state[TttState.CurrentScreen] = TttScreen.OpponentName
            case TttScreen.OpponentName:
                match data:
                    case "x":
                        state[TttState.CurrentScreen] = TttScreen.Main
                    case _:
                        # setup a fresh game
                        state[TttState.CurrentScreen] = TttScreen.Game
                        state[TttState.GamesByOpponentName][data] = dict[str, str]()
                        state[TttState.CurrentOpponentName] = data
                        state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.PlayerPiece] = TttBoardSquareState.PlayerOne
                        state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.Board] = [ TttBoardSquareState.Empty, TttBoardSquareState.Empty, TttBoardSquareState.Empty, \
                                                                                                    TttBoardSquareState.Empty, TttBoardSquareState.Empty, TttBoardSquareState.Empty, \
                                                                                                    TttBoardSquareState.Empty, TttBoardSquareState.Empty, TttBoardSquareState.Empty ]
                        state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.CurrenTurnPlayer] = TttBoardSquareState.PlayerOne
            case TttScreen.Game:
                 match data:
                    case "x":
                        state[TttState.CurrentScreen] = TttScreen.Main
                    case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8":
                        available_positions = []
                        for index, square in enumerate(state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.Board]):
                            match square:
                                case TttBoardSquareState.Empty:
                                    available_positions.append(str(index))
                        if data in available_positions:
                            position = int(data)
                            state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.Board][position] = state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.PlayerPiece]
                            state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.CurrenTurnPlayer] = TttBoardSquareState.PlayerTwo
                            square_descriptions = []
                            for square in state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.Board]:
                                match square:
                                    case TttBoardSquareState.Empty:
                                        square_descriptions.append(" ")
                                    case TttBoardSquareState.PlayerOne:
                                        square_descriptions.append("X")
                                    case TttBoardSquareState.PlayerTwo:
                                        square_descriptions.append("O")
                            board_description = "".join(square_descriptions)
                            host.send_remote_command(sender_short_name, state[TttState.CurrentOpponentName], board_description)
        # print updated options
        match state[TttState.CurrentScreen]:
            case TttScreen.Main:
                output_lines.append("[C]reate new game")
                if len(state[TttState.GamesByOpponentName]) > 0:
                    output_lines.append("[V]iew existing games")
            case TttScreen.OpponentName:
                output_lines.append("Opponent's short name?")
            case TttScreen.Game:
                # print board
                board_display = []
                available_positions = []
                for index, square in enumerate(state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.Board]):
                    match square:
                        case TttBoardSquareState.Empty:
                            board_display.append(str(index))
                            available_positions.append(str(index))
                        case TttBoardSquareState.PlayerOne:
                            board_display.append("X")
                        case TttBoardSquareState.PlayerTwo:
                            board_display.append("O")
                    match index:
                        case 0 | 1 | 3 | 4 | 6 | 7:
                            board_display.append(" | ")
                        case 2 | 5 :
                            board_display.append("\n---------\n")
                        case 8:
                            board_display.append("\n")
                output_lines.append("".join(board_display))
                # print options
                is_local_players_turn = state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.CurrenTurnPlayer] == state[TttState.GamesByOpponentName][state[TttState.CurrentOpponentName]][TttState.PlayerPiece]
                if len(available_positions) == 0:
                    # end game reached
                    # TODO: determine who won
                    output_lines.append("Someone won!... maybe.")
                elif is_local_players_turn:
                    output_lines.append("Where do you want to place your piece?\n(" + ", ".join(available_positions) + ")")
                    
        output_lines.append("e[X]it")


        # print the output
        output = "\n".join(output_lines)
        host.print_local(sender_short_name, output)

        # save the state for next time
        serialised_state = json.dumps(state)
        host.store_state(sender_short_name, serialised_state)

    def try_process_remote_command(host: DoorHost, sender_short_name: str, recipient_short_name : str, data: str) -> bool:
        pass