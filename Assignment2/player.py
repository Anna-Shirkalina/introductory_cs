"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    total_num_players = num_human + num_random + len(smart_players)
    ids = list(range(total_num_players))
    goals = generate_goals(total_num_players)
    player_list = []
    for i in range(num_human):
        player = HumanPlayer(ids[i], goals[i])
        player_list.append(player)
    for i in range(num_random):
        j = num_human + i
        player = RandomPlayer(ids[j], goals[j])
        player_list.append(player)
    for i, difficulty in enumerate(smart_players):
        j = num_human + num_random + i
        player = SmartPlayer(ids[j], goals[j], difficulty)
        player_list.append(player)
    return player_list


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    if not _location_in_block(block, location):
        return None
    if level == block.level:
        if _location_in_block(block, location):
            return block
        else:
            return None
    elif not block.children:
        if _location_in_block(block, location):
            return block
        else:
            return None
    else:
        sub_block = block
        for child in block.children:
            if _location_in_block(child, location):
                sub_block = child
        return _get_block(sub_block, location, level)


def _location_in_block(block: Block, location: Tuple[int, int]) -> bool:
    """Return True if the location is within the block, false otherwise

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    >>>bock = Block((0, 0), 10, (199, 44, 58), 0, 1)
    >>>location1 = (9, 0)
    >>>_location_in_block(block, location1)
    True
    >>>location2 = (10, 0)
    >>>_location_in_block(block, location2)
    False
    """
    x = location[0]
    y = location[1]
    x_0 = block.position[0]
    y_0 = block.position[1]
    x_n = x_0 + block.size - 1
    y_n = y_0 + block.size - 1
    if not x_0 <= x <= x_n:
        return False
    if not y_0 <= y <= y_n:
        return False
    return True



class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, min(self._level, board.max_depth))

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    """A random player

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.

    === Private Attributes ===
    _proceed:
            This is a boolean that indicates if the player should proceed
            with and action
    """
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        actions_list = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE,
                        SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT, COMBINE]
        board_copy = board.create_copy()
        block = _random_block_generator(board_copy)
        random.shuffle(actions_list)
        act = actions_list[0]
        for acts in actions_list:
            if _check_valid_actions(acts, block, self.goal):
                act = acts
                break
        self._proceed = False  # Must set to False before returning!
        return act


def _check_valid_actions(action: Tuple[str, Optional[int]],
                         block: Block, goal: Goal) -> bool:
    """Return True if the action is a valid action for block, return false
     otherwise"""
    if action == ROTATE_CLOCKWISE:
        direction = ROTATE_CLOCKWISE[1]
        return block.rotate(direction)
    if action == ROTATE_COUNTER_CLOCKWISE:
        direction = ROTATE_COUNTER_CLOCKWISE[1]
        return block.rotate(direction)
    if action == SWAP_HORIZONTAL:
        direction = SWAP_HORIZONTAL[1]
        return block.swap(direction)
    if action == SWAP_VERTICAL:
        direction = SWAP_VERTICAL[1]
        return block.swap(direction)
    if action == SMASH:
        return block.smash()
    if action == PAINT:
        return block.paint(goal.colour)
    if action == COMBINE:
        return block.combine()
    else:
        return False


def _random_block_generator(board: Block) -> Block:
    """Return a new random block within the board at a random position and
    a random level"""

    size = board.size
    x = random.randint(0, size - 1)
    y = random.randint(0, size - 1)
    level = random.randint(0, board.max_depth)
    random_block = _get_block(board, (x, y), level)
    return random_block


class SmartPlayer(Player):
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    """A random player

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    difficulty:
            The higher the difficulty, the better the smart player

    === Private Attributes ===
    _proceed:
            This is a boolean that indicates if the player should proceed
            with and action
    """
    difficulty: int
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self.difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        copy_board = board.create_copy()
        actions_list = [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE,
                        SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT, COMBINE]
        random.shuffle(actions_list)
        valid_actions = []
        while len(valid_actions) < self.difficulty:
            for acts in actions_list:
                copy_board = board.create_copy()
                block = _random_block_generator(copy_board)
                if _check_valid_actions(acts, block, self.goal):
                    score = self.goal.score(copy_board)
                    valid_actions.append((acts, block, score))
        self._proceed = False  # Must set to False before returning!
        action, block = self._find_best_move(valid_actions, copy_board)
        return _create_move(action, block)

    def _find_best_move(self, valid_moves: List[Tuple[Tuple[str,
                                                            Optional[int]]],
                                                Block, int], board: Block) -> \
            Tuple[Tuple[str, Optional[int]], Block]:
        """Return the move from valid_moves with the highest score, if the
        current score is higher than any score from the resulting moves then
        the move PASS will be returned"""
        scores = [valid_moves[i][2] for i in range(len(valid_moves))]
        highest_score = max(scores)
        if highest_score > self.goal.score(board):
            index = scores.index(highest_score)
            block = valid_moves[index][1]
            return valid_moves[index][0], block
        else:
            return PASS, valid_moves[0][1]



#if __name__ == '__main__':
    #import python_ta

    # python_ta.check_all(config={
    #     'allowed-io': ['process_event'],
    #     'allowed-import-modules': [
    #         'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
    #         'goal', 'pygame', '__future__'
    #     ],
    #     'max-attributes': 10,
    #     'generated-members': 'pygame.*'
    # })
