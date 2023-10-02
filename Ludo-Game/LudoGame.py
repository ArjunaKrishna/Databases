class Player:
    """A class to represent a player who plays the game at a certain position. Contains an init method for
    initializing a few data members and uses different methods. """

    def __init__(self, position):
        """Takes no parameters and initializes the required private data members to None. """
        self._position = position
        self._token_start = None
        self._end = None
        self._current_position = None
        self._current_state = None
        self._token_position = ["p", "q"]

    def get_token_start(self):
        """Gets the starting position of the token. Used by the LudoGame class to get the token start. """
        return self._token_start

    def get_completed(self):
        """Takes no parameters. Returns true or false depending on whether the player has finished the game or not. """
        if self._current_state == "playing":
            return False
        if self._current_state == "finished":
            return True

    def get_position(self):
        """Gets the position of the player. Used by the LudoGame class to get the player."""
        return self._position

    def set_token_position(self, token_position, token_name):
        """Sets the token position. Used by the LudoGame class to set the token position at a specific value. """
        self._token_position[token_name] = token_position

    def get_token_position(self):
        """Gets the token_position of the player. """
        return self._token_position

    def get_token_p_step_count(self):
        """Gets the step_count of p or in other words how much token p has moved. """
        if self._token_start != None:
            return ((self._token_position[0]) - (self._token_start))

    def get_token_q_step_count(self):
        """Gets the step_count of q or in other words how much token q has moved. """
        if self._token_start != None:
            return ((self._token_position[1]) - (self._token_start))

    def get_p_current_position(self):
        return self._p.current_position

    def get_q_current_position(self):
        return self._q.current_position

    def get_space_name(self, total_steps):

        if total_steps == -1:
            return 'H'
        if total_steps == 0:
            return 'R'
        if total_steps == 57:
            return 'E'
        if self._token_start == 1:
            if total_steps <= 50:
                return str(total_steps)
            if total_steps > 50:
                return 'A' + str(total_steps - 50)
        if self._token_start == 15:
            if total_steps <= 50:
                return str(15 + total_steps)
            if total_steps > 56:
                return str(total_steps - 57 + 15)
            if total_steps > 50:
                return 'B' + str(total_steps - 50)
        if self._token_start == 29:
            if total_steps <= 50:
                return str(29 + total_steps)
            if total_steps > 56:
                return str(total_steps - 57 + 29)
            if total_steps > 50:
                return 'C' + str(total_steps - 50)
        if self._token_start == 43:
            if total_steps <= 50:
                return str(43 + total_steps)
            if total_steps > 56:
                return str(total_steps - 57 + 43)
            if total_steps > 50:
                return 'D' + str(total_steps - 50)

class LudoGame:

    def __init__(self):
        """Takes no parameters and initializes the required private data members to None. """
        self._board = None
        self._list_of_players = []

    def get_player_by_position(self, player_position):
        """Takes a parameter representing the player’s position as a string and returns the player object. For an invalid string parameter,
           it will return 'Player not found!'"""
        for player in self._list_of_players:
                if player.get_space_name (player.get_token_p_step_count()) == player_position:
                    return player
                elif player.get_space_name (player.get_token_q_step_count()) == player_position:
                    return player

        return "Player not Found!"

    def move_priority(self, move_steps, player):
        """Implements the rules like when the player can move or not move. Has four priority rules:"""

        # Priority rule 1
        # If the die roll is 6, try to let the token that still in the home yard get out of the home yard (if both tokens are in the home yard,
        # choose the first one ‘p’).

        if move_steps == 6:
            if player.get_p_current_position() == "H":
                return "p"
            elif player.get_q_current_position() == "H":
                return "q"

        # Priority rule 2
        # If one token is already in the home square and the step number is exactly what is needed to reach the end square, let that token move.
        # and finish

        if player.get_token_p_step_count() >= 50:
            if player.get_token_p_step_count() + move_steps == 57:
                return "p"

        if player.get_token_q_step_count() >= 50:
            if player.get_token_q_step_count() + move_steps == 57:
                return "q"

        # Priority rule 3
        # If one token can move and kick out an opponent token, then move that token.

        # Current position of p. It gets the space name of the current position + the die roll

        p_current_position = player.get_space_name(player.get_token_p_step_count() + move_steps)
        opponent = player.get_player_by_position(p_current_position, player)
        if player.get_player_by_position(p_current_position, player) != "Player Not Found":
            if opponent.get_p_current_position() == p_current_position:
                opponent.set_token_position("H", 0)
                return "p"

        q_current_position = player.get_space_name(player.get_token_q_step_count() + move_steps)
        opponent = player.get_player_by_position(q_current_position, player)
        if player.get_player_by_position(q_current_position, player) != "Player Not Found":
            if opponent.get_q_current_position() == q_current_position:
                opponent.set_token_position("H", 0)
                return "q"

        p_current_position = player.get_space_name(player.get_token_p_step_count() + move_steps)
        opponent = player.get_player_by_position(q_current_position, player)
        if player.get_player_by_position(q_current_position, player) != "Player Not Found":
            if opponent.get_q_current_position() == p_current_position:
                opponent.set_token_position("H", 0)
                return "p"

        q_current_position = player.get_space_name(player.get_token_q_step_count() + move_steps)
        opponent = player.get_player_by_position(p_current_position, player)
        if player.get_player_by_position(p_current_position, player) != "Player Not Found":
            if opponent.get_p_current_position() == q_current_position:
                opponent.set_token_position("H", 0)
                return "q"

        # Current position of q. It gets the space name of the current position + the die roll

        q_current_position = player.get_space_name(player.get_token_q_step_count() + move_steps)
        # q_opponent_token_position
        if player.get_player_by_position(p_current_position, player) != "Player Not Found":
            return "q"
        q_opponent_token_position = "H"
        q_opponent_step_count = -1

            # Priority rule 4
        # Move the token that is further away from the finishing square.

        #it basically makes sure that one token isn't moved through the game without moving the second token (unless the second token
        # never gets a 6 to leave the home base)
        # If the second token hasn't moved, then the first token doesn't move.

        if player.get_token_p_step_count() == -1 and player.get_token_q_step_count() == -1:
            pass

        if player.get_token_p_step_count() == 0 and player.get_token_q_step_count() == -1:
            return "p"

        if player.get_token_p_step_count() == -1 and player.get_token_q_step_count() == 0:
            return "q"

        if player.get_token_p_step_count() > player.get_token_q_step_count():
            return "q"

        if player.get_token_p_step_count() < player.get_token_q_step_count():
            return "p"

    def move_token(self, player, token_name, move_steps):
        """Takes three parameters, the player object, the token name, and the steps the token will move on the board. This method will take care of
           one token moving on the board. It will also update the token’s total steps, and it will take care of kicking out other opponent tokens as
           needed. The play_game method will use this method. """

        var = token_name
        if token_name == "p":
            total_steps = player.get_token_p_step_count()
            var = 0

        if token_name == "q":
            total_steps = player.get_token_q_step_count()
            var = 1

        # When two tokens get stacked on each other, return the other one which went on the top.
        if player.get_token_q_step_count + move_steps == player.get_token_p_step_count:
            return "q"

        if player.get_token_p_step_count + move_steps == player.get_token_q_step_count:
            return "p"

        # When in the intermediate space, the normal addition of steps is done depending on the token either p or q.
        if total_steps + move_steps <= 50:
            player.set_token_position(str((total_steps + move_steps)), var)

        # When the token p is in the home row and if the step count equals to the finishing position, it sets the position of the token to the finished row.
        if total_steps + move_steps > 50:
            if token_name == "p":
                if player.get_token_p_step_count() + (57 - player.get_token_p_step_count) == 57:
                    player.set_token_position(total_steps + move_steps)
            if token_name == "q":
                if player.get_token_q_step_count() + (57 - player.get_token_q_step_count) == 57:
                    player.set_token_position(total_steps + move_steps)

        # When in the home row, concatenated strings like A1, B2, C3, or D4 are displayed depending on the number of players.
        if total_steps + move_steps >= 50:
            if player.get_token_start() == 1:
                player.set_token_position(str('A' + (total_steps + move_steps) - 50), var)
            if player.get_token_start() == 15:
                player.set_token_position(str('B' + (total_steps + move_steps) - 50), var)
            if player.get_token_start() == 29:
                player.set_token_position(str('C' + (total_steps + move_steps) - 50), var)
            if player.get_token_start() == 43:
                player.set_token_position(str('D' + (total_steps + move_steps) - 50), var)

        # When a token moves from the intermediate space to the home row, strings are concatenated for each player's token p and q.
        if total_steps + move_steps <= 50:
            end_position = total_steps + move_steps
            if end_position > 57:
                if token_name == "p":
                    if player.get_token_start() == 1:
                        player.set_token_position(str('A' + (player.get_token_p_step_count() + (end_position - player.get_token_p_step_count()) + (move_steps - (end_position - player.get_token_p_step_count()))) - 50), var)
                    if player.get_token_start() == 15:
                        player.set_token_position(str('B' + (player.get_token_p_step_count() + (end_position - player.get_token_p_step_count()) + (move_steps - (end_position - player.get_token_p_step_count()))) - 50), var)
                    if player.get_token_start() == 29:
                        player.set_token_position(str('C' + (player.get_token_p_step_count() + (end_position - player.get_token_p_step_count()) + (move_steps - (end_position - player.get_token_p_step_count()))) - 50), var)
                    if player.get_token_start() == 43:
                        player.set_token_position(str('D' + (player.get_token_p_step_count() + (end_position - player.get_token_p_step_count()) + (move_steps - (end_position - player.get_token_p_step_count()))) - 50), var)
                if token_name == "q":
                    if player.get_token_start() == 1:
                        player.set_token_position(str('A' + (player.get_token_q_step_count() + (end_position - player.get_token_q_step_count()) + (move_steps - (end_position - player.get_token_q_step_count()))) - 50), var)
                    if player.get_token_start() == 15:
                        player.set_token_position(str('B' + (player.get_token_q_step_count() + (end_position - player.get_token_q_step_count()) + (move_steps - (end_position - player.get_token_q_step_count()))) - 50), var)
                    if player.get_token_start() == 29:
                        player.set_token_position(str('C' + (player.get_token_q_step_count() + (end_position - player.get_token_q_step_count()) + (move_steps - (end_position - player.get_token_q_step_count()))) - 50), var)
                    if player.get_token_start() == 43:
                        player.set_token_position(str('D' + (player.get_token_q_step_count() + (end_position - player.get_token_q_step_count()) + (move_steps - (end_position - player.get_token_q_step_count()))) - 50), var)

    def play_game(self, players_list, turns_list):
        """Takes two parameters, the players list, and the turns list. The players list is the list of positions players choose, like [‘A’, ‘C’] means
           two players will play the game at position A and C. Turns list is a list of tuples with each tuple a roll for one player. For example, [('A', 6),
           ('A', 4), ('C', 5)] means player A rolls 6, then rolls 4, and player C rolls 5. This method will create the player list first using the players
           list pass in, and then move the tokens according to the turns list following the priority rule and update the tokens position and the player’s
           game state (whether finished the game or not). After all the moving is done in the turns list, the method will return a list of strings
           representing the current spaces of all the tokens for each player in the list after moving the tokens following the rules described above.
           ‘H’ for home yard, ‘R’ for ready to go position, ‘E’ for finished position, and other letters/numbers for the space the token has landed on."""

        for player in players_list:
            self._list_of_players.append(Player(player))

        for some_turn in turns_list:
            display_list = []
            for thing in self._list_of_players:
                display_list.append(thing.get_space_name(thing.get_token_p_step_count()))
                display_list.append(thing.get_space_name(thing.get_token_q_step_count()))
            print(display_list)

            for thing in self._list_of_players:
                player_name = some_turn[0]
                roll_of_player = some_turn[1]
                if thing.get_position() == player_name:
                    player = thing
                    priority_method = self.move_priority(player, roll_of_player)
                    self.move_token(player, priority_method, roll_of_player, self._list_of_players)

