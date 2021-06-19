BOARD_FILES = 'abcdefgh'
BOARD_RANKS = '87654321'

to_move = 'w'
board = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R'],
]
castling_rights = 'KQkq'

pawn_forward_moves = [
    'a3','b3','c3','d3','e3','f3','g3','h3',
    'a4','b4','c4','d4','e4','f4','g4','h4',
    'a5','b5','c5','d5','e5','f5','g5','h5',
    'a6','b6','c6','d6','e6','f6','g6','h6',
    'a7','b7','c7','d7','e7','f7','g7','h7',
]

pawn_takes_moves = [
    
]

pawn_forward_promotion_moves = [
    'a8=Q','b8=Q','c8=Q','d8=Q','e8=Q','f8=Q','g8=Q','h8=Q'
    'a1=Q','b1=Q','c1=Q','d1=Q','e1=Q','f1=Q','g1=Q','h1=Q'
]


def get_index_from_square(square):
    square_file = BOARD_FILES.index(square[0])
    square_rank = BOARD_RANKS.index(square[1])
    return square_file, square_rank

def get_piece_from_square(square, board):
    index_file, index_rank = get_index_from_square(square)
    return board[index_rank][index_file]

def get_piece_from_index(index, board):
    index_file, index_rank = index
    return board[index_rank][index_file]

def index_to_square(coords):
    index_file, index_rank = coords
    square_rank = BOARD_RANKS[index_rank]
    square_file = BOARD_FILES[index_file]
    return f'{square_file}{square_rank}'

def clear_coords(square, board):
    square_file, square_rank = square
    board[square_rank][square_file] = '-'

def fill_coords(square, board, piece):
    square_file, square_rank = square
    board[square_rank][square_file] = piece

def print_board(board):
    for row in board:
        print(row)

def pawn_is_taking(move):
    if len(move) != 4:
        return False
    if move[0] not in BOARD_FILES:
        return False
    if move[1] != 'x':
        return False
    if move[2] not in BOARD_FILES:
        return False
    return move[3] in BOARD_RANKS

def pawn_is_moving_forward_without_promoting(move):
    return move in pawn_forward_moves

def is_pawn_move(move):
    return any([
        pawn_is_moving_forward_without_promoting(move),
        pawn_is_taking(move)        
    ])

def get_end_square(move):
    return move[2:] if 'x' in move else move

def get_pawn_start_coords(move, board, player):
    end_square = get_end_square(move)
    end_coords_file, end_coords_rank = get_index_from_square(end_square)
    preceding_rank = end_coords_rank + 1 if player == 'w' else end_coords_rank - 1
    if pawn_is_moving_forward_without_promoting(move):
        preceding_file = end_coords_file
        if get_piece_from_index((preceding_file, preceding_rank),board).lower() != 'p':
            preceding_rank = end_coords_rank + 2 if player == 'w' else end_coords_rank - 2
        return preceding_file, preceding_rank
    elif pawn_is_taking(move):
        preceding_file = BOARD_FILES.index(move[0])
        return preceding_file, preceding_rank

def clear_en_passant_coords_if_necessary(move, board, player):
    end_square = get_end_square(move)
    end_coords = get_index_from_square(end_square)
    end_coords_file, end_coords_rank = end_coords
    en_passant_rank = end_coords_rank + 1 if player == 'w' else end_coords_rank - 1
    en_passant_coords = (end_coords_file, en_passant_rank)
    if get_piece_from_index(end_coords, board) == '-':
        clear_coords(en_passant_coords, board)
    
def process_move(move, board, player):
    end_coords = (-1,-1)
    start_coords = (-1,-1)
    piece = '-'
    if is_pawn_move(move):
        piece = 'P' if player == 'w' else 'p'
        start_coords = get_pawn_start_coords(move, board, player)
        print(start_coords)
    if pawn_is_moving_forward_without_promoting(move):
        end_coords = get_index_from_square(move)
    elif pawn_is_taking(move):
        print('PAWN IS TAKING')
        end_square = get_end_square(move)
        end_coords = get_index_from_square(end_square)
        clear_en_passant_coords_if_necessary(move, board, player)
    clear_coords(start_coords, board)
    fill_coords(end_coords, board, piece)
    print()
    print_board(board)
    pass

print_board(board)

moves = ['e4', 'e5', 'd4', 'exd4','c4','dxc3']

for idx, move in enumerate(moves):
    process_move(move, board, 'w' if idx % 2 == 0 else 'b')

