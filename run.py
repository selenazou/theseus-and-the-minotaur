'''
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from nnf import Var

SUMMARY OF FUNCTIONS/BRIEF CODE DOCUMENTATION HERE: https://docs.google.com/document/d/1cW7keLwbJXumtzpbQCZ_Dcds2fXrwDSy-KxJAeD6IaA/edit
'''
import random

# Encoding that will store all of your constraints
#E = Encoding()

# GLOBAL VARIABLES
# Board size
BOARD_SIZE = 6

# we might use this for walls and for possible moves for Theseus or Minotaur
DIRECTIONS = ['top', 'bottom', 'left', 'right']

# Number of turns and hedges
NUM_ROUNDS = random.randint(10, 20)
NUM_HEDGES = random.randint(5, 40)


# OOP for the board
class Board_Square:

  def __init__(self, x, y):
    '''
    self: the object being instantiated
    x, y: coordinate pair, INTS
    top, bottom, left, and right describe the side of the square where a hedge might be
    (true if there is a hedge, false if not)
    t_x,y and m_x,y describe Theseus's and the Minotaur's positions respectively
    EXIT_x,y describe the exit square
    '''
    self.x = x
    self.y = y
    self.top = False
    self.bottom = False
    self.left = False
    self.right = False
    self.t_x = False
    self.t_y = False
    self.m_x = False
    self.m_y = False
    self.EXIT_x = False
    self.EXIT_y = False

  # returns a tuple representation of a (row, col) coordinate on the board
  def board_loc(self):
    return tuple([self.x, self.y])


# Initializes a list to hold positions of hedges
def hedge_grid():
  grid = []
  for i in range(BOARD_SIZE):
    row = []
    for j in range(BOARD_SIZE):
      row.append(False)
    grid.append(row)
  return grid


def set_hedges():
    '''
    Set the hedges (mini-walls) inside the maze. Generate some random number of hedges at some random
    squares, then choose some random direction for each hedge.
    '''
    # 2D arrays for hedge locations and directions
    vert_hedges_bool = hedge_grid()  # T if hedge at right side of square, F if not
    hor_hedges_bool = hedge_grid()  # T is hedge at top of square, F if not

    # Generate coordinates and directions for hedges.
    # For each hedge, generate 2 coordinates and one direction.
    for i in range(NUM_HEDGES):
        row = random.randint(0, BOARD_SIZE - 1)
        col = random.randint(0, BOARD_SIZE - 1)
        dir = DIRECTIONS[random.randint(0, 3)]

        if dir == 'left' and col-1 >= 0:
            vert_hedges_bool[row][col - 1] = True
        elif dir == 'right':
            vert_hedges_bool[row][col] = True
        elif dir == 'top':
            hor_hedges_bool[row][col] = True
        elif dir == 'bottom' and row+1 < 6:
            hor_hedges_bool[row + 1][col] = True
    return vert_hedges_bool, hor_hedges_bool


def start_board():
    '''
    Defines starting locations for Theseus and the Minotaur, as well as
    a (permanent) exit location and hedges.
    '''
    t_start_x = random.randint(0, BOARD_SIZE-1)
    t_start_y = random.randint(0, BOARD_SIZE-1)
    m_start_x = random.randint(0, BOARD_SIZE-1)
    m_start_y = random.randint(0, BOARD_SIZE-1)
    EXIT_x = random.randint(0, BOARD_SIZE-1)
    EXIT_y = random.randint(0, BOARD_SIZE-1)
    # get the hedges here
    VERT_HEDGES, HOR_HEDGES = set_hedges()
    # initialize the board to have x, y coords and everything else False
    board = []
    for x in range(BOARD_SIZE):
        row = []
        for y in range(BOARD_SIZE):
            square = Board_Square(x, y)
            if x == t_start_x and y == t_start_y:
                square.t_x = True
                square.t_y = True
            if x == m_start_x and y == m_start_y:
                square.m_x = True
                square.m_y = True
            if x == EXIT_x and y == EXIT_y:
                square.EXIT_x = True
                square.EXIT_y = True
            if VERT_HEDGES[x][y]:  # hedge to the right
                square.right = True
            if HOR_HEDGES[x][y]:  #hedge to top
                square.top = True
            row.append(square)
        board.append(row)
    # set left and bottom hedges - if (x,y) has hedge to right, (x,y+1) has hedge to left
    # and if (x,y) has hedge on top, (x-1, y) has hedge on bottom
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y].right and y + 1 < BOARD_SIZE:
                board[x][y + 1].left = True
            if board[x][y].top and x - 1 >= 0:
                board[x - 1][y].bottom = True
    return board, t_start_x, t_start_y, m_start_x, m_start_y, EXIT_x, EXIT_y, VERT_HEDGES, HOR_HEDGES


def set_board(board, t_x, t_y, m_x, m_y):
    '''
    Set the board to the current game state.
    The only things that will ever change are t_x, t_y, m_x, and m_y.
    If this function is called, Theseus and the Minotaur will never be
    on the same square.
    t_x: Theseus' new x-position, t_y: Theseus' new y-position (both ints)
    m_x: Minotaur's new x-pos, m_y: Minotaur's new y-pos (both ints)
    '''
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
        # first set the old Theseus and Minotaur squares to False
            if board[x][y].t_x and board[x][y].t_y:
                board[x][y].t_x = False
                board[x][y].t_y = False
            elif board[x][y].m_x and board[x][y].m_y:
                board[x][y].m_x = False
                board[x][y].m_y = False
            # now check if this square is the new Theseus/Minotaur square and set it to True
            if x == t_x and y == t_y:
                board[x][y].t_x = True
                board[x][y].t_y = True
            elif x == m_x and y == m_y:
                board[x][y].m_x = True
                board[x][y].m_y = True
    return board


def thes_win(board, t_row, t_col):
    '''
    Determines if Theseus has won the game by checking whether his square is
    the same as the exit square and if the Minotaur is not there.
    @param: board (2D array of Board_Square objects) describing the current game state
    @param: t_row, t_col (ints), Theseus's current x,y position
    '''
    if board[t_row][t_col].EXIT_x and board[t_row][t_col].EXIT_y:
        return True
    return False


def thes_eaten(t_row, t_col, m_row, m_col):
    '''
    Determines if Theseus has been eaten by the Minotaur by checking
    whether his square is the same as the Minotaur's.
    @param: t_row, t_col (ints), Theseus' current x,y position
    @param: m_row, m_col (ints), Minotaur's current x,y position
    '''
    if t_row == m_row and t_col == m_col:
        return True
    return False


def within_borders(target_row, target_col):
    """
    @param: target_row (int), row index of square being queried
    @param: target_col (int), col index of square being queried
    @return: True if square in board, False otherwise
    """
    #Sierra's attempt
    #if the target row index is 6 or more
    if target_row >= BOARD_SIZE:
        return False
    #if the target row index is less than 0 (wants to move up out of the maze)
    elif target_row < 0:
        return False
    #if the target column index is 6 or more
    elif target_col >= BOARD_SIZE:
        return False
    #if the target column index is less than 0
    elif target_col < 0:
        return False
    else:
        return True


def mino_within_range(targ_row, targ_col, m_row, m_col):
    '''
    @param: targ_row, targ_col (ints), x,y position being queried
    @param: m_row, m_col (ints), current x,y position of Minotaur
    @return: False if position not within range of Minotaur (+/- 2 squares in 1 direction),
    or 1 square diagonally; True otherwise
    '''
    # Target square within 2 up, 2 down, 2 left, or 2 right of Minotaur
    if ((abs(targ_row - m_row) <= 2 and targ_col == m_col)
        or (abs(targ_col - m_col) <= 2 and targ_row == m_row)):
        return True
    # Target square is one diagonal from Minotaur
    if (abs(targ_row - m_row) == 1 and abs(targ_col - m_col) == 1):
        return True
    return False


def mino_hedges_in_way(board, targ_row, targ_col, m_row, m_col):
    '''
    Find if there are hedges between the Minotaur's current position and his
    target position. NOTE: ALSO USABLE FOR DETERMINING IF THESEUS IS SAFE BY CHECKING
    MINOTAUR PATHS WHEN HE IS <3 SQUARES FROM MINOTAUR
    @param: targ_row, targ_col (ints), x,y position of target square
    @param: m_row, m_col (ints), x,y of Minotaur's current position
    @return: True if there are hedges in the way, False otherwise
    '''
    # Target square above Minotaur
    if targ_row == m_row - 2 and targ_col == m_col:
        if board[m_row][m_col].top or board[m_row - 1][m_col].top:
            return True
            # if the first conditional evaluates to True and the nested if to False, we can return False by default
        return False
    elif targ_row == m_row - 1 and targ_col == m_col:
        if board[m_row][m_col].top:
            return True
        return False
    # Target square below
    elif targ_row == m_row + 1 and targ_col == m_col:
        if board[m_row][m_col].bottom:
            return True
        return False
    elif targ_row == m_row + 2 and targ_col == m_col:
        if board[m_row][m_col].bottom or board[m_row + 1][m_col].bottom:
            return True
        return False
    # Target square left
    elif targ_row == m_row and targ_col == m_col - 2:
        if board[m_row][m_col].left or board[m_row][m_col - 1].left:
            return True
        return False
    elif targ_row == m_row and targ_col == m_col - 1:
        if board[m_row][m_col].left:
            return True
        return False
    # Target square right
    elif targ_row == m_row and targ_col == m_col + 1:
        if board[m_row][m_col].right:
            return True
        return False
    elif targ_row == m_row and targ_col == m_col + 2:
        if board[m_row][m_col].right or board[m_row][m_col + 1].right:
            return True
        return False

    # Target up and to the left
    elif targ_row == m_row - 1 and targ_col == m_row - 1:
        if board[targ_row][targ_col].bottom and (board[targ_row][targ_col].right
                                                or board[m_row][m_col].top):
            return True
        elif board[m_row][m_col].left and (board[m_row][m_col].top
                                        or board[targ_row][targ_col].right):
            return True
        return False
    # Target up and to right
    elif targ_row == m_row - 1 and targ_col == m_col + 1:
        if board[targ_row][targ_col].bottom and (board[targ_row][targ_col].left
                                                or board[m_row][m_col].top):
            return True
        elif board[m_row][m_col].right and (board[m_row][m_col].top
                                            or board[targ_row][targ_col].left):
            return True
        return False
    # Target down and to left
    elif targ_row == m_row + 1 and targ_col == m_col - 1:
        if board[targ_row][targ_col].top and (board[targ_row][targ_col].right
                                            or board[m_row][m_col].bottom):
            return True
        elif board[m_row][m_col].left and (board[m_row][m_col].bottom
                                        or board[targ_row][targ_col].right):
            return True
        return False
    # Target down and to right
    elif targ_row == m_row + 1 and targ_col == m_col + 1:
        if board[targ_row][targ_col].top and (board[targ_row][targ_col].left
                                            or board[m_row][m_col].bottom):
            return True
        elif board[m_row][m_col].right and (board[m_row][m_col].bottom
                                            or board[targ_row][targ_col].left):
            return True
        return False

    # I don't know if we need to even set a default case because this function should
    # cover all cases of Minotaur moving squares, but we can always remove it
    return False


def mino_move(board, mino_row, mino_col, thes_row, thes_col):
    """
    Defines the Minotaur's move according to the algorithm below.
    Minotaur cannot move out of the board or cross a wall.
    Minotaur will always try to move closer to Theseus. If he can do so by moving horizontally,
    he will move horizontally. He will move vertically iff he cannot get closer to Theseus by moving
    horizontally.
    @param: board (2D array of Board_Square objects), describes current game state
    @param: mino_row (int), Minotaur's current row position
    @param: mino_col (int), Minotaur's col position
    @param: thes_row (int), Theseus' row position
    @param: thes_col (int), Theseus' col position
    @return: a (row, col) tuple of the Minotaur's valid move
    """
    row_diff = mino_row - thes_row
    col_diff = mino_col - thes_col
    # First check horizontal moves
    # Theseus to right of Minotaur
    if col_diff < 0 and not mino_hedges_in_way(board, mino_row, mino_col + 1,
                                                mino_row, mino_col):
        # The Minotaur should move one square to the right
        return tuple([mino_row, mino_col + 1])
    # Theseus to left of Minotaur
    elif col_diff > 0 and not mino_hedges_in_way(board, mino_row, mino_col - 1,
                                                mino_row, mino_col):
        # The Minotaur should move one square to the left
        return tuple([mino_row, mino_col - 1])
    # Otherwise, the Minotaur can't get closer to Theseus by moving horizontally, so he tries
    # to move vertically. If he moves vertically and gets closer to Theseus, row_diff should decrease.
    else:  # includes col_diff == 0
        # Theseus below the Minotaur
        if row_diff < 0 and not mino_hedges_in_way(board, mino_row + 1, mino_col,
                                                mino_row, mino_col):
            # Minotaur should move one down
            return tuple([mino_row + 1, mino_col])
        # Theseus above the Minotaur
        elif row_diff > 0 and not mino_hedges_in_way(board, mino_row - 1, mino_col,
                                                    mino_row, mino_col):
            # Minotaur should move one up
            return tuple([mino_row - 1, mino_col])
    # If none of the above work, the Minotaur skips his turn.
    return tuple([mino_row, mino_col])


def theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                        target_row, target_col):
    '''
    Defines constraints on Theseus' moves.
    Theseus cannot move out of the board or cross a wall.
    Theseus cannot move to a square that is within the Minotaur's reach.
    @param: board (2D array of Board_Square objects) describing current game state
    @param: thes_row (int), Theseus' row position
    @param: thes_col (int), Theseus' col position
    @param: mino_row (int), Minotaur's row position
    @param: mino_col (int), Minotaur's col position
    @param: target_row (int), row index of square being queried for Theseus' move
    @param: target_col(int), column index of square being queried for Theseus' move
    @return: True if Theseus can move to [row, col], False otherwise
    '''
    # Check if the target square is out of bounds
    if not within_borders(target_row, target_col):
        return False

    # Check if there are hedges preventing Theseus from moving to the target square.
    # Target square 1 to right of Theseus' current position.
    if target_row == thes_row and target_col == thes_col + 1 and board[
        thes_row][thes_col].right:
        return False
    # Target square 1 to left
    elif target_row == thes_row and target_col == thes_col - 1 and board[
        thes_row][thes_col].left:
        return False
    # Target square 1 up
    elif target_row == thes_row - 1 and target_col == thes_col and board[
        thes_row][thes_col].top:
        return False
    # Target square 1 down
    elif target_row == thes_row + 1 and target_col == thes_col and board[
        thes_row][thes_col].bottom:
        return False

    # DON'T-GET-EATEN CONSTRAINTS HERE #

    # Check if Theseus is moving onto the Minotaur's square... obviously bad idea
    if target_row == mino_row and target_col == mino_col:
        return False

    # Check if Theseus is moving onto the exit - then we don't need to check
    # if the Minotaur is in range
    if thes_win(board, target_row, target_col):
        return True

    # Theseus can move within 2 squares horizontally or vertically or 1 square diagonally of
    # Minotaur and be safe if there are hedges between him and the Minotaur.
    if mino_within_range(target_row, target_col, mino_row, mino_col):
        if not mino_hedges_in_way(board, target_row, target_col, mino_row,
                                mino_col):
            return False

    # If we reach this point, the square is OK.
    return True


def theseus_moves(board, thes_row, thes_col, mino_row, mino_col):
    '''
    Determine the valid moves for Theseus, using constraints determined
    by theseus_constraints().
    @param: board (2D array of Board_Square objects), describes the current game state
    @param: thes_row, thes_col (ints), Theseus' current x,y position
    @param: mino_row, mino_col (ints), Minotaur's current x,y position
    @return: a list of (row, col) tuples of valid moves for Theseus. NOTE THAT
    IF THE RETURNED LIST IS EMPTY, THESEUS LOSES.
    '''
    # Theseus can move to 4 different squares, or remain in his spot (skip his turn).
    moves = []
    # Move up or down
    if theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                            thes_row - 1, thes_col):
        moves.append(tuple([thes_row - 1, thes_col]))
    if theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                            thes_row + 1, thes_col):
        moves.append(tuple([thes_row + 1, thes_col]))
    # Move left or right
    if theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                            thes_row, thes_col + 1):
        moves.append(tuple([thes_row, thes_col + 1]))
    if theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                            thes_row, thes_col - 1):
        moves.append(tuple([thes_row, thes_col - 1]))
    if theseus_constraints(board, thes_row, thes_col, mino_row, mino_col,
                            thes_row, thes_col):
        moves.append(tuple([thes_row, thes_col]))
    return moves


def is_winnable(board, t_row, t_col, m_row, m_col, exit_x, exit_y, round_num=0):
    '''
    Determines recursively whether Theseus can win, given a certain board configuration.
    Base Cases:
    1. Theseus has won (his position is the exit square) and Minotaur's position is not exit square. Return True.
    2. Theseus has been eaten (his position is the Minotaur's). Return False.
    3. Theseus has run out of moves and loses (round_num = NUM_ROUNDS). Return False.
    (Generate a list of Theseus' viable moves here)
    4. Theseus has no viable moves (his move list is empty). Return False.
    Else:
    5. Theseus has viable moves. Loop over the moves in the list.
    General structure: Have Theseus make a move. Then have the Minotaur make two based on his algorithm. Then
    return a recursive call to this function to determine whether Theseus can win.
    REMEMBER TO INCREMENT THE ROUND NUMBER.
    @param: board (2D array of Board_Square objects) describing current board configuration
    @param: t_row, t_col (ints), describe Theseus' current x,y position
    @param: m_row, m_col (ints), describe Minotaur's current x,y position
    @param: round_num (int), the round the game is on (increments each time this function runs)
    @return: Boolean (True if Theseus can win, False otherwise)
    '''
    # If Theseus has been eaten by the Minotaur
    if thes_eaten(t_row, t_col, m_row, m_col):
        return False
    # If Theseus' position is the exit and the Minotaur is not there
    if thes_win(board, t_row, t_col):
        return True
    # Theseus has run out of turns
    if round_num >= NUM_ROUNDS:
        return False
    else:
        moves = theseus_moves(board, t_row, t_col, m_row, m_col)
        # If the moves list is empty
        if not moves:
            return False
        else:
            # We already validated the moves list so that no moves that get Theseus
            # eaten immediately are included, so if the exit square is in the moves list,
            # he wins
            if tuple([exit_x, exit_y]) in moves:
                return True
            # Check each move in the moves list
            move = moves[0]
            while moves:
                # Have Theseus move once and the Minotaur move twice
                t_new_row, t_new_col = move[0], move[1]
                m_turn1 = mino_move(board, m_row, m_col, t_new_row, t_new_col)
                m_turn2 = mino_move(board, m_turn1[0], m_turn1[1], t_new_row, t_new_col)
                m_new_row, m_new_col = m_turn2[0], m_turn2[1]
                # Set the board according to new positions and increment the round number by 1
                board = set_board(board, t_new_row, t_new_col, m_new_row, m_new_col)
                round_num += 1
                # If Theseus can eventually win, return True - no need to check anything else
                if is_winnable(board, t_new_row, t_new_col, m_new_row, m_new_col, exit_x, exit_y, round_num):
                    return True
                # If Theseus can't win with this move, go on to the next move
                else:
                    round_num -= 1
                    moves.remove(move)
                    if moves:
                        move = moves[0]



def game():
  '''
  Main function to pull it all together.
  Some key points:
    1. Initialize the board with everyone's starting places, permanent fixtures like hedges and exit.
    2. Have Theseus move first. For every move Theseus makes, the Minotaur makes two.
        Use is_winnable() function for this. (Remember to multiply NUM_ROUNDS by 3.)
    3. The return value of is_winnable determines the outcome of the game.
  '''
  # Initialize everything
  board, t_x, t_y, m_x, m_y, exit_x, exit_y, vert_h, hor_h = start_board()
  #print("Theseus' starting position: ", tuple([t_x,t_y]))
  #print("Minotaur's starting position: ", tuple([m_x,m_y]))
  #print("EXIT: ", tuple([exit_x, exit_y]))

  # Print some representations
  arr = hedge_grid()
  for row in range(BOARD_SIZE):
      for col in range(BOARD_SIZE):
          if board[row][col].t_x and board[row][col].t_y:
              arr[row][col] = "T"
          elif board[row][col].m_x and board[row][col].m_y:
              arr[row][col] = "M"
          elif board[row][col].EXIT_x and board[row][col].EXIT_y:
              arr[row][col] = "E"
          else:
              arr[row][col] = "*"
  print("starting board:")
  for row in arr:
      print(row)

  print()
  
  for row in range(BOARD_SIZE):
      for col in range(BOARD_SIZE):
          if vert_h[row][col]:
              vert_h[row][col] = "T"
          else:
              vert_h[row][col] = "F"
              
  print("vertical hedges:")
  for row in vert_h:
      print(row)
  print()

  for row in range(BOARD_SIZE):
      for col in range(BOARD_SIZE):
          if hor_h[row][col]:
              hor_h[row][col] = "T"
          else:
              hor_h[row][col] = "F"
  print("horizontal hedges:")
  for row in hor_h:
      print(row)
  
  
  print("NUM_ROUNDS: ", NUM_ROUNDS)
  
  turn_num = 0
  if is_winnable(board, t_x, t_y, m_x, m_y, exit_x, exit_y, turn_num):
    print("Theseus wins!")
  else:
    print("Theseus got eaten by the Minotaur :(")

game()
