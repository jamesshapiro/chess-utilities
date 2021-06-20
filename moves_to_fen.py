import math
import sys

BOARD_FILES = 'abcdefgh'
BOARD_RANKS = '87654321'

reference_board = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','-','-','-','-'],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R'],
]

test_board = [
    ['b','n','r','q','k','-','r','r'],
    ['p','p','p','p','p','p','-','p'],
    ['-','-','-','-','-','-','-','q'],
    ['-','-','-','-','-','-','p','-'],
    ['-','-','-','-','-','-','-','-'],
    ['-','-','-','-','K','-','-','-'],
    ['P','P','P','P','P','P','p','P'],
    ['R','N','B','Q','R','B','N','R'],
]


def clone_board(board):
    new_board = []
    for row in board:
        new_board.append(row[:])
    return new_board

board = clone_board(reference_board)

castling_rights = {
    'white_kingside': True,
    'white_queenside': True,
    'black_kingside': True,
    'black_queenside': True,
}

misc_data = {
    'en_passant_target': '-',
    'halfmove_clock': 0
}

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


def get_coords_from_square(square):
    square_file = BOARD_FILES.index(square[0])
    square_rank = BOARD_RANKS.index(square[1])
    return square_file, square_rank

def get_piece_from_coords(board, index):
    index_file, index_rank = index
    return board[index_rank][index_file]

def index_to_square(coords):
    index_file, index_rank = coords
    square_rank = BOARD_RANKS[index_rank]
    square_file = BOARD_FILES[index_file]
    return f'{square_file}{square_rank}'

def clear_coords(board, coords):
    square_file, square_rank = coords
    board[square_rank][square_file] = '-'

def fill_coords(board, square, piece):
    square_file, square_rank = square
    board[square_rank][square_file] = piece

icon_table = {
    'K': '♔',
    'Q': '♕',
    'R': '♖',
    'B': '♗',
    'N': '♘',
    'P': '♙',
    'k': '♚',
    'q': '♛',
    'r': '♜',
    'b': '♝',
    'n': '♞',
    'p': '♟'
}
    
def print_board(board):
    for row in board:
        #print_row = [icon_table.get(piece, piece) for piece in row]
        print(''.join(row))

def print_castling_rights(castling_rights):
    result = ''
    result += 'K' if castling_rights['white_kingside'] else ''
    result += 'Q' if castling_rights['white_queenside'] else ''
    result += 'k' if castling_rights['black_kingside'] else ''
    result += 'q' if castling_rights['black_queenside'] else ''
    if result:
        print(result)
        
def pawn_is_taking_without_promoting(move):
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
        pawn_is_taking_without_promoting(move)        
    ])

def get_end_square(move):
    move = move.replace('+','')
    if '=' not in move:
        return move[-2:]
    print('TODO: implement promotion')
    sys.exit(0)

def get_pawn_start_coords(board, move, player):
    move = move.replace('+','')
    end_square = get_end_square(move)
    end_coords_file, end_coords_rank = get_coords_from_square(end_square)
    preceding_rank = end_coords_rank + 1 if player == 'w' else end_coords_rank - 1
    if pawn_is_moving_forward_without_promoting(move):
        preceding_file = end_coords_file
        if get_piece_from_coords(board, (preceding_file, preceding_rank)).lower() != 'p':
            preceding_rank = end_coords_rank + 2 if player == 'w' else end_coords_rank - 2
        return preceding_file, preceding_rank
    elif pawn_is_taking_without_promoting(move):
        preceding_file = BOARD_FILES.index(move[0])
        return preceding_file, preceding_rank

def clear_en_passant_coords_if_necessary(board, move, player):
    end_square = get_end_square(move)
    end_coords = get_coords_from_square(end_square)
    end_coords_file, end_coords_rank = end_coords
    en_passant_rank = end_coords_rank + 1 if player == 'w' else end_coords_rank - 1
    en_passant_coords = (end_coords_file, en_passant_rank)
    if get_piece_from_coords(board, end_coords) == '-':
        clear_coords(board, en_passant_coords)

def get_piece_coords(board, piece, color):
    all_coords = []
    piece_key = piece.upper() if color == 'w' else piece.lower()
    for rank_index, rank_row in enumerate(board):
        for file_index, square in enumerate(rank_row):
            if square == piece_key:
                all_coords.append((file_index, rank_index))
    return all_coords

def get_king_coords(board, player):
    return get_piece_coords(board, 'k', player)[0]

def get_bishop_coords(board, color):
    return get_piece_coords(board, 'b', color)

def get_knight_coords(board, color):
    return get_piece_coords(board, 'n', color)

def get_rook_coords(board, color):
    return get_piece_coords(board, 'r', color)

def get_queen_coords(board, color):
    return get_piece_coords(board, 'q', color)

def get_pawn_coords(board, color):
    return get_piece_coords(board, 'p', color)

def get_radius(coords, candidate_deltas):
    coords_file, coords_rank = coords
    candidate_squares = [(coords_file + x, coords_rank + y) for x,y in candidate_deltas]
    candidate_squares = [(x,y) for x,y in candidate_squares if x >= 0 and x < 8 and y >= 0 and y < 8]
    return candidate_squares
    

def get_knight_radius(coords):
    candidate_deltas = [(1,2),(2,1),(1,-2),(-2,1),(-1,2),(2,-1),(-1,-2),(-2,-1)]
    return get_radius(coords, candidate_deltas)

def get_bishop_radius(coords):
    candidate_deltas = [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)]
    negative   = [(-x, -y) for x,y in candidate_deltas]
    negative_x = [(-x,  y) for x,y in candidate_deltas]
    negative_y = [( x, -y) for x,y in candidate_deltas]
    candidate_deltas = [*candidate_deltas, *negative, *negative_x, *negative_y]
    return get_radius(coords, candidate_deltas)

def get_rook_radius(coords):
    candidate_deltas = [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0)]
    negative   = [(-x, y) for x,y in candidate_deltas]
    candidate_deltas = [*candidate_deltas, *negative]
    flipped    = [(y,x)   for x,y in candidate_deltas]
    candidate_deltas = [*candidate_deltas, *flipped]
    return get_radius(coords, candidate_deltas)

def get_queen_radius(coords):
    bishop_radius = get_bishop_radius(coords)
    rook_radius = get_rook_radius(coords)
    return [*bishop_radius, *rook_radius]

def get_pawn_radius(coords, color):
    direction = -1 if color == 'w' else 1
    candidate_deltas = [(-1,direction), (1, direction)]
    return get_radius(coords, candidate_deltas)

def get_king_radius(coords):
    candidate_deltas = [
        (-1,-1),(0,-1),(1,-1),
        (-1,0),        (1,0),
        (-1,1), (0, 1),(1,1)
    ]
    return get_radius(coords, candidate_deltas)

def bishop_can_reach_square(board, bishop_coords, square_coords):
    bishop_file, bishop_rank = bishop_coords
    square_file, square_rank = square_coords
    file_difference = bishop_file - square_file
    rank_difference = bishop_rank - square_rank
    if abs(file_difference) != abs(rank_difference):
        return False
    rank_direction = int(math.copysign(1,rank_difference))
    file_direction = int(math.copysign(1,file_difference))
    for i in range(1, abs(rank_difference)):
        new_coords = (bishop_file - (i * file_direction), bishop_rank - (i * rank_direction))
        if get_piece_from_coords(board, new_coords) != '-':
            return False
    return True

def bishop_checks_king(board, bishop_coords, king_coords):
    return bishop_can_reach_square(board, bishop_coords, king_coords)

def rook_can_reach_square(board, rook_coords, square_coords):
    rook_file, rook_rank = rook_coords
    square_file, square_rank = square_coords
    file_difference = rook_file - square_file
    rank_difference = rook_rank - square_rank
    if min(abs(file_difference), abs(rank_difference)) != 0:
        return False
    rook_is_same_rank = square_rank == rook_rank
    direction = int(math.copysign(1, rank_difference)) 
    if rook_is_same_rank:
        direction = int(math.copysign(1, file_difference))
    for i in range(1, max(abs(file_difference), abs(rank_difference))):
        file_increment = direction if rook_is_same_rank else 0
        rank_increment = direction if not rook_is_same_rank else 0
        new_coords = (rook_file - (i * file_increment), rook_rank - (i * rank_increment))
        if get_piece_from_coords(board, new_coords) != '-':
            return False
    return True
    
def rook_checks_king(board, rook_coords, king_coords):
    return rook_can_reach_square(board, rook_coords, king_coords)

def queen_can_reach_square(board, queen_coords, square_coords):
    return any([
        bishop_can_reach_square(board, queen_coords, square_coords),
        rook_can_reach_square(board, queen_coords, square_coords)
    ])
    
def queen_checks_king(board, queen_coords, king_coords):
    return queen_can_reach_square(board, queen_coords, king_coords)

def king_is_in_check(board, player):
    player_king = 'K' if player == 'w' else 'k'
    player_king_coords = get_king_coords(board, player)
    opp_color = 'b' if player == 'w' else 'w'
    opp_pawn_coords = get_pawn_coords(board, opp_color)
    opp_knight_coords = get_knight_coords(board, opp_color)
    opp_king_coords = get_king_coords(board, opp_color)
    opp_bishop_coords = get_bishop_coords(board, opp_color)
    opp_rook_coords = get_rook_coords(board, opp_color)
    opp_queen_coords = get_queen_coords(board, opp_color)
    unsafe_squares = []
    for pawn_coords in opp_pawn_coords:
        unsafe_squares.extend(get_pawn_radius(pawn_coords, opp_color))
    for knight_coords in opp_knight_coords:
        unsafe_squares.extend(get_knight_radius(knight_coords))
    unsafe_squares.extend(get_king_radius(opp_king_coords))
    for unsafe_square in unsafe_squares:
        if get_piece_from_coords(board, unsafe_square) == player_king:
            return True
    for bishop_coords in opp_bishop_coords:
        if bishop_checks_king(board, bishop_coords, player_king_coords):
            return True
    for rook_coords in opp_rook_coords:
        if rook_checks_king(board, rook_coords, player_king_coords):
            return True
    for queen_coords in opp_queen_coords:
        if queen_checks_king(board, queen_coords, player_king_coords):
            return True
    return False

def move_piece(board, start_coords, end_coords, piece):
    clear_coords(board, start_coords)
    fill_coords(board, end_coords, piece)

def get_knight_start_coords(board, move, end_coords, player, piece, *misc):
    move = move.replace('x','')
    move = move.replace('+','')
    if len(move) == 5:
        return get_coords_from_square(move[1:3])
    knight_radius = get_knight_radius(end_coords)
    knight_coords = get_knight_coords(board, player)
    knight_candidates = list(set(knight_radius) & set(knight_coords))
    if len(move) == 4:
        specifier = move[1]
        if specifier in BOARD_FILES:
            specified_file = BOARD_FILES.index(specifier)
            knight_candidates = [candidate for candidate in knight_candidates if candidate[0] == specified_file]
        else:
            specified_rank = BOARD_RANKS.index(specifier)
            knight_candidates = [candidate for candidate in knight_candidates if candidate[1] == specified_rank]
    for candidate in knight_candidates:
        board_clone = clone_board(board)
        move_piece(board_clone, candidate, end_coords, piece)
        if not king_is_in_check(board_clone, player):
            return candidate

def get_brq_start_coords(board, move, end_coords, get_radius_fn, brq_can_reach_fn, player, piece):
    move = move.replace('x','')
    move = move.replace('+','')
    if len(move) == 5:
        return get_coords_from_square(move[1:3])
    brq_radius = get_radius_fn(end_coords)
    brq_coords = get_piece_coords(board, piece, player)
    brq_candidates = list(set(brq_radius) & set(brq_coords))
    if len(move) == 4:
        specifier = move[1]
        if specifier in BOARD_FILES:
            specified_file = BOARD_FILES.index(specifier)
            brq_candidates = [candidate for candidate in brq_candidates if candidate[0] == specified_file]
        else:
            specified_rank = BOARD_RANKS.index(specifier)
            brq_candidates = [candidate for candidate in brq_candidates if candidate[1] == specified_rank]
    brq_candidates = list(filter(lambda x: brq_can_reach_fn(board, x, end_coords), brq_candidates))
    for candidate in brq_candidates:
        board_clone = clone_board(board)
        move_piece(board_clone, candidate, end_coords, piece)
        if not king_is_in_check(board_clone, player):
            return candidate

def get_bishop_start_coords(board, move, end_coords, player, piece, *misc):
    return get_brq_start_coords(
        board, move, end_coords, get_bishop_radius,
        bishop_can_reach_square, player, piece
    )
    
def get_rook_start_coords(board, move, end_coords, player, piece, castling_rights):
    start_coords = get_brq_start_coords(
        board, move, end_coords, get_rook_radius,
        rook_can_reach_square, player, piece
    )
    if player == 'w' and start_coords == (0,7):
        disable_castling_rights(player, castling_rights, kingside=False, queenside=True)
    elif player == 'w' and start_coords == (7,7):
        disable_castling_rights(player, castling_rights, kingside=True, queenside=False)
    elif player == 'b' and start_coords == (0,0):
        disable_castling_rights(player, castling_rights, kingside=False, queenside=True)
    elif player == 'b' and start_coords == (7,0):
        disable_castling_rights(player, castling_rights, kingside=True, queenside=False)
    return start_coords
    
def get_queen_start_coords(board, move, end_coords, player, piece, *misc):
    return get_brq_start_coords(
        board, move, end_coords, get_queen_radius,
        queen_can_reach_square, player, piece
    )

move_fn_map = {
    'N': get_knight_start_coords,
    'B': get_bishop_start_coords,
    'R': get_rook_start_coords,
    'Q': get_queen_start_coords
}

def castle(board, player, castling_rights, is_kingside):
    king = 'K' if player == 'w' else 'k'
    rook = 'R' if player == 'w' else 'r'
    rank = BOARD_RANKS.index('1') if player == 'w' else BOARD_RANKS.index('8')
    clear_castle_file = 'h' if is_kingside else 'a'
    new_king_file = 'g' if is_kingside else 'c'
    new_castle_file = 'f' if is_kingside else 'd'
    clear_coords(board, (BOARD_FILES.index('e'), rank))
    clear_coords(board, (BOARD_FILES.index(clear_castle_file), rank))
    fill_coords(board, (BOARD_FILES.index(new_king_file), rank), king)
    fill_coords(board, (BOARD_FILES.index(new_castle_file), rank), rook)
    disable_castling_rights(player, castling_rights, kingside=True, queenside=True)
    print_board(board)
    print_castling_rights(castling_rights)

def is_castles(move):
    return move in ['O-O','O-O-O']

def is_king_move(move):
    return move[0] == 'K'

def disable_castling_rights(player, castling_rights, kingside, queenside):
    if player == 'w':
        castling_rights['white_kingside'] &= not kingside
        castling_rights['white_queenside'] &= not queenside
    else:
        castling_rights['black_kingside'] &= not kingside
        castling_rights['black_queenside'] &= not queenside
    
def process_move(board, move, player, castling_rights, misc_data):
    misc_data['halfmove_clock'] += 1
    if 'x' in move:
        misc_data['halfmove_clock'] = 0
    misc_data['en_passant_target'] = '-'
    if is_castles(move):
        if move == 'O-O':
            castle(board, player, castling_rights, is_kingside=True)
        else:
            castle(board, player, castling_rights, is_kingside=False)
        return
    end_square = get_end_square(move)
    end_coords = get_coords_from_square(end_square)
    start_coords = (-1,-1)
    piece = move[0].upper() if player == 'w' else move[0].lower()
    if is_pawn_move(move):
        misc_data['halfmove_clock'] = 0
        piece = 'P' if player == 'w' else 'p'
        start_coords = get_pawn_start_coords(board, move, player)
        start_coords_file = start_coords[0]
        end_coords_file = end_coords[0]
        if start_coords_file == end_coords_file and abs(start_coords[1] - end_coords[1]) == 2:
            misc_data['en_passant_target'] = index_to_square((start_coords[0], min(start_coords[1], end_coords[1]) + 1))
        if pawn_is_taking_without_promoting(move):
            clear_en_passant_coords_if_necessary(board, move, player)
    elif move[0] in move_fn_map:
        start_coords = move_fn_map[move[0]](board, move, end_coords, player, piece, castling_rights)
    elif is_king_move(move):
        start_coords = get_king_coords(board, player)
        disable_castling_rights(player, castling_rights, kingside=True,queenside=True)

    move_piece(board, start_coords, end_coords, piece)
    print_board(board)
    print_castling_rights(castling_rights)
    pass

print_board(board)
print()

#moves = ["e4", "d5", "exd5", "Qxd5", "Qf3", "Qxf3", "Nxf3", "Nf6", "Bc4", "Nc6", "d3", "Bf5", "Nc3", "O-O-O", "O-O", "Na5", "Bb3", "Nxb3", "axb3", "Kb8", "Be3", "b6", "Nb5", "a5", "c3", "Bc8", "b4", "Ba6", "c4", "Bxb5", "cxb5", "Rxd3", "bxa5", "bxa5", "Rxa5", "Rb3", "Rfa1", "Kc8", "Bd4", "e6", "Bc3", "Bd6", "Nd4", "Kd7", "Nxb3", "Nd5", "Nd4", "Nxc3", "bxc3", "Ke7", "c4", "Kf6", "Nc6", "Bc5", "Ra6", "Bb6", "R6a4", "Bc5", "Rc1", "Re8", "Rd1", "e5", "Nd8", "Bd6", "Nc6", "Bc5", "Rd5", "Bb6", "Ra6", "Bd4", "Nxd4+", "Ke7", "Nf3"]
moves = ["e4", "d5", "exd5", "Qxd5", "Qf3", "Qxf3", "Nxf3", "Nf6", "Bc4", "Nc6", "d3", "Bf5", "Nc3", "O-O-O", "O-O", "Na5", "Bb3", "Nxb3", "axb3", "Kb8", "Be3", "b6", "Nb5", "a5", "c3", "Bc8", "b4", "Ba6", "c4", "Bxb5", "cxb5", "Rxd3", "bxa5", "bxa5", "Rxa5", "Rb3", "Rfa1", "Kc8", "Bd4", "e6", "Bc3", "Bd6", "Nd4", "Kd7", "Nxb3", "Nd5", "Nd4", "Nxc3", "bxc3", "Ke7", "c4", "Kf6", "Nc6", "Bc5", "Ra6", "Bb6", "R6a4", "Bc5", "Rc1", "Re8", "Rd1", "e5", "Nd8", "Bd6", "Nc6", "Bc5", "Rd5", "Bb6", "Ra6", "Bd4", "Nxd4+", "Ke7", "Nf3"]

for idx, move in enumerate(moves):
    print()
    print(f'{idx+1}   {move}')
    print('++++++++')
    print()
    process_move(board, move, 'w' if idx % 2 == 0 else 'b', castling_rights, misc_data)
    #print(misc_data)
    print()

def get_fen_notation(board, move_num, castling_rights):
    pass
    
    
"""
print()
print()
print()


print_board(test_board)
"""
