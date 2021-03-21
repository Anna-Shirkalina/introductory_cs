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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    num = random.random()
    goal_list = []
    colours = _get_goal_colours()
    if num < 0.5:
        for i in range(num_goals):
            colour = colours[i]
            goal = PerimeterGoal(colour)
            goal_list.append(goal)
    else:
        for i in range(num_goals):
            colour = colours[i]
            goal = BlobGoal(colour)
            goal_list.append(goal)
    return goal_list


def _get_goal_colours() -> List[Tuple[int, int, int]]:
    """Return a list of randomly shuffled colours for the next goal in
    goal_list
    >>>my_lst = _get_goal_colours()
    [REAL_RED, PACIFIC_POINT, DAFFODIL_DELIGHT, OLD_OLIVE]
    >>>new_lst = _get_goal_colours()
    [DAFFODIL_DELIGHT, REAL_RED, OLD_OLIVE, PACIFIC_POINT]
    """
    colour_lst = COLOUR_LIST[:]
    random.shuffle(colour_lst)
    return colour_lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.level == block.max_depth:
        return [[block.colour]]
    elif not block.children:
        dim = int(2 ** (block.max_depth - block.level))
        return [[block.colour] * dim for _ in range(dim)]
    else:
        grid = []
        child_grid_0 = _flatten(block.children[0])
        child_grid_1 = _flatten(block.children[1])
        child_grid_2 = _flatten(block.children[2])
        child_grid_3 = _flatten(block.children[3])
        dim = 2 * len(child_grid_1)
        i = 0
        while i < dim:
            if i < dim / 2:
                column = child_grid_1[i][:] + child_grid_2[i][:]
                grid.append(column)
            else:
                j = int(i - dim/2)
                column = child_grid_0[j][:] + child_grid_3[j][:]
                grid.append(column)
            i += 1
        return grid


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """This is a child of the class Goal.
    The PerimeterGoal sets a goal which is to maximize the number of unit cells
    of a given colour along the perimeter

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    def score(self, board: Block) -> int:
        """Return the score for the perimeter goal, score is calculated based
        on how many unit blocks are touching the perimeter"""
        grid = _flatten(board)
        left = grid[0]
        right = grid[-1]
        top = [i[0] for i in grid]
        bottom = [i[-1] for i in grid]
        score0 = left.count(self.colour)
        score1 = right.count(self.colour)
        score2 = top.count(self.colour)
        score3 = bottom.count(self.colour)
        return score0 + score1 + score2 + score3


    def description(self) -> str:
        """Returns the description for the PerimeterGoal class"""
        return f'Maximize number of {colour_name(self.colour)} unit cells on ' \
               f'the perimeter, corner cells count double'


class BlobGoal(Goal):
    """A child class of the class Goal
    This BlobGoal is to maximize the blob of a given colour

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    def score(self, board: Block) -> int:
        """Return the score of the BlobGoal, calculated based on the
        largest connected blob of the same colour"""
        board = _flatten(board)
        dim = len(board)
        visited = [[-1] * dim for _ in range(dim)]
        max_score = 0
        for i in range(dim):
            for j in range(dim):
                blob_at_ij = self._undiscovered_blob_size((i, j), board,
                                                          visited)
                max_score = max(max_score, blob_at_ij)
        return max_score

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x_0 = pos[0]
        y_0 = pos[1]
        if x_0 > len(board) - 1 or y_0 > len(board) - 1:
            return 0
        if visited[x_0][y_0] != -1:
            return 0
        if board[x_0][y_0] != self.colour:
            visited[x_0][y_0] = 0
            return 0
        else:
            visited[x_0][y_0] = 1
            size0 = self._undiscovered_blob_size((x_0, y_0 + 1), board, visited)
            size1 = self._undiscovered_blob_size((x_0, y_0 - 1), board, visited)
            size2 = self._undiscovered_blob_size((x_0 + 1, y_0), board, visited)
            size3 = self._undiscovered_blob_size((x_0 - 1, y_0), board, visited)
            return size0 + size1 + size2 + size3 + 1


    def description(self) -> str:
        """Returns the description for the PerimeterGoal class"""
        return f"Maximize number of {colour_name(self.colour)} unit cells " \
               f"that form a blob by touching sides. " \
               f"Touching corners doesn't count"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
