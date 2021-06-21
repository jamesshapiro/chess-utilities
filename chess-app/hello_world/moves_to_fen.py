import math
import sys

BOARD_FILES = 'abcdefgh'
BOARD_RANKS = '87654321'
WHITE_KING = 'K'
WHITE_QUEEN = 'Q'
WHITE_ROOK = 'R'
WHITE_BISHOP = 'B'
WHITE_KNIGHT = 'N'
WHITE_PAWN = 'P'
BLACK_KING = 'k'
BLACK_QUEEN = 'q'
BLACK_ROOK = 'r'
BLACK_BISHOP = 'b'
BLACK_KNIGHT = 'n'
BLACK_PAWN = 'p'
KING='k'
QUEEN='q'
ROOK='r'
BISHOP='b'
KNIGHT='n'
PAWN='p'
EMPTY = '-'
BLACK = 'b'
WHITE = 'w'

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

icon_table = {
    'K': '♔','Q': '♕','R': '♖','B': '♗','N': '♘','P': '♙',
    'k': '♚','q': '♛','r': '♜','b': '♝','n': '♞','p': '♟'
}

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
    'en_passant_target': EMPTY,
    'halfmove_clock': 0
}

def get_coords_from_square(square):
    square_file = BOARD_FILES.index(square[0])
    square_rank = BOARD_RANKS.index(square[1])
    return square_file, square_rank

def get_piece_from_coords(board, index):
    index_file, index_rank = index
    return board[index_rank][index_file]

def coords_to_squarecoords):
    index_file, index_rank = coords
    square_rank = BOARD_RANKS[index_rank]
    square_file = BOARD_FILES[index_file]
    return f'{square_file}{square_rank}'

def clear_coords(board, coords):
    square_file, square_rank = coords
    board[square_rank][square_file] = EMPTY

def fill_coords(board, square, piece):
    square_file, square_rank = square
    board[square_rank][square_file] = piece

def print_board(board):
    for row in board:
        #row = [icon_table.get(piece, piece) for piece in row]
        print(' '.join(row))

def get_castling_rights(castling_rights):
    result = ''
    result += WHITE_KING if castling_rights['white_kingside'] else ''
    result += WHITE_QUEEN if castling_rights['white_queenside'] else ''
    result += BLACK_KING if castling_rights['black_kingside'] else ''
    result += BLACK_QUEEN if castling_rights['black_queenside'] else ''
    if result:
        return result
    return EMPTY
        
def pawn_is_taking(move):
    return move[0] in BOARD_FILES and move[1] == 'x'

def pawn_is_moving_forward(move):
    move = move.replace('+','')
    if move[0] in BOARD_FILES and move[1] in BOARD_RANKS:
        return True

def is_pawn_move(move):
    return move[0] in BOARD_FILES

def get_end_square(move):
    move = move.replace('+','')
    if '=' not in move:
        return move[-2:]
    if 'x' in move:
        return move[2:4]
    return move[:2]

def get_pawn_start_coords(board, move, player):
    move = move.replace('+','')
    end_square = get_end_square(move)
    end_coords_file, end_coords_rank = get_coords_from_square(end_square)
    preceding_rank = end_coords_rank + 1 if player == WHITE else end_coords_rank - 1
    # The logic here checks if the pawn moved forward two moves our not
    if pawn_is_moving_forward(move):
        preceding_file = end_coords_file
        if get_piece_from_coords(board, (preceding_file, preceding_rank)).lower() != 'p':
            preceding_rank = end_coords_rank + 2 if player == WHITE else end_coords_rank - 2
        return preceding_file, preceding_rank
    elif pawn_is_taking(move):
        preceding_file = BOARD_FILES.index(move[0])
        return preceding_file, preceding_rank

def clear_en_passant_coords_if_necessary(board, move, player):
    end_square = get_end_square(move)
    end_coords = get_coords_from_square(end_square)
    end_coords_file, end_coords_rank = end_coords
    en_passant_rank = end_coords_rank + 1 if player == WHITE else end_coords_rank - 1
    en_passant_coords = (end_coords_file, en_passant_rank)
    if get_piece_from_coords(board, end_coords) == EMPTY:
        clear_coords(board, en_passant_coords)

def get_piece_coords(board, color, piece=KING):
    all_coords = []
    piece_key = piece.upper() if color == WHITE else piece.lower()
    for rank_index, rank_row in enumerate(board):
        for file_index, square in enumerate(rank_row):
            if square == piece_key:
                all_coords.append((file_index, rank_index))
    return all_coords

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
    direction = -1 if color == WHITE else 1
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
        if get_piece_from_coords(board, new_coords) != EMPTY:
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
        if get_piece_from_coords(board, new_coords) != EMPTY:
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
    player_king = WHITE_KING if player == WHITE else BLACK_KING
    player_king_coords = get_piece_coords(board, player, piece=KING)[0]
    opp_color = BLACK if player == WHITE else WHITE
    opp_pawn_coords = get_piece_coords(board, opp_color, piece=PAWN)
    opp_knight_coords = get_piece_coords(board, opp_color, piece=KNIGHT)
    opp_king_coords = get_piece_coords(board, opp_color, piece=KING)[0]
    opp_bishop_coords = get_piece_coords(board, opp_color, piece=BISHOP)
    opp_rook_coords = get_piece_coords(board, opp_color, piece=ROOK)
    opp_queen_coords = get_piece_coords(board, opp_color, piece=QUEEN)
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
    knight_coords = get_piece_coords(board, player, piece='n')
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
    brq_coords = get_piece_coords(board, player, piece=piece)
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
    if player == WHITE and start_coords == get_coords_from_square('a1'):
        revoke_castling_rights(player, castling_rights, revoke_kingside=False, revoke_queenside=True)
    elif player == WHITE and start_coords == get_coords_from_square('h1'):
        revoke_castling_rights(player, castling_rights, revoke_kingside=True, revoke_queenside=False)
    elif player == BLACK and start_coords == get_coords_from_square('a8'):
        revoke_castling_rights(player, castling_rights, revoke_kingside=False, revoke_queenside=True)
    elif player == BLACK and start_coords == get_coords_from_square('h8'):
        revoke_castling_rights(player, castling_rights, revoke_kingside=True, revoke_queenside=False)
    return start_coords
    
def get_queen_start_coords(board, move, end_coords, player, piece, *misc):
    return get_brq_start_coords(
        board, move, end_coords, get_queen_radius,
        queen_can_reach_square, player, piece
    )

move_fn_map = {
    KNIGHT.upper(): get_knight_start_coords,
    BISHOP.upper(): get_bishop_start_coords,
    ROOK.upper(): get_rook_start_coords,
    QUEEN.upper(): get_queen_start_coords
}

def castle(board, player, castling_rights, is_kingside):
    king = WHITE_KING if player == WHITE else BLACK_KING
    rook = WHITE_ROOK if player == WHITE else BLACK_ROOK
    rank = BOARD_RANKS.index('1') if player == WHITE else BOARD_RANKS.index('8')
    clear_castle_file = 'h' if is_kingside else 'a'
    new_king_file = 'g' if is_kingside else 'c'
    new_castle_file = 'f' if is_kingside else 'd'
    clear_coords(board, (BOARD_FILES.index('e'), rank))
    clear_coords(board, (BOARD_FILES.index(clear_castle_file), rank))
    fill_coords(board, (BOARD_FILES.index(new_king_file), rank), king)
    fill_coords(board, (BOARD_FILES.index(new_castle_file), rank), rook)
    revoke_castling_rights(player, castling_rights, revoke_kingside=True, revoke_queenside=True)
    print_board(board)

def is_castles(move):
    return move in ['O-O','O-O-O']

def is_king_move(move):
    return move[0] == KING.upper()

def revoke_castling_rights(player, castling_rights, revoke_kingside, revoke_queenside):
    if player == WHITE:
        castling_rights['white_kingside'] &= not revoke_kingside
        castling_rights['white_queenside'] &= not revoke_queenside
    else:
        castling_rights['black_kingside'] &= not revoke_kingside
        castling_rights['black_queenside'] &= not revoke_queenside
    
def process_move(board, move, player, castling_rights, misc_data):
    if 'resigned' in move:
        sys.exit(0)
    misc_data['halfmove_clock'] += 1
    if 'x' in move:
        misc_data['halfmove_clock'] = 0
    misc_data['en_passant_target'] = EMPTY
    if is_castles(move):
        if move == 'O-O':
            castle(board, player, castling_rights, is_kingside=True)
        else:
            castle(board, player, castling_rights, is_kingside=False)
        return
    end_square = get_end_square(move)
    end_coords = get_coords_from_square(end_square)
    start_coords = (-1,-1)
    piece = move[0].upper() if player == WHITE else move[0].lower()
    if is_pawn_move(move):
        misc_data['halfmove_clock'] = 0
        piece = WHITE_PAWN if player == WHITE else 'p'
        if end_coords[1] in [0,7]:
            piece = move.replace('+','')[-1]
            piece = piece.upper() if player == WHITE else piece.lower()
        start_coords = get_pawn_start_coords(board, move, player)
        start_coords_file = start_coords[0]
        end_coords_file = end_coords[0]
        if start_coords_file == end_coords_file and abs(start_coords[1] - end_coords[1]) == 2:
            misc_data['en_passant_target'] = coords_to_square(start_coords[0], min(start_coords[1], end_coords[1]) + 1))
        if pawn_is_taking(move):
            clear_en_passant_coords_if_necessary(board, move, player)
    elif move[0] in move_fn_map:
        start_coords = move_fn_map[move[0]](board, move, end_coords, player, piece, castling_rights)
    elif is_king_move(move):
        start_coords = get_piece_coords(board, player, piece=KING)[0]
        revoke_castling_rights(player, castling_rights, revoke_kingside=True, revoke_queenside=True)
    move_piece(board, start_coords, end_coords, piece)
    print_board(board)
    pass

print_board(board)
print()

moves = ["e4", "e6", "d4", "d5", "e5", "c5", "c3", "Nc6", "Nf3", "Nge7", "Be3", "Nf5", "Qd2", "Nxe3", "Qxe3", "Be7", "Be2", "O-O", "O-O", "f6", "b3", "fxe5", "Nxe5", "Nxe5", "Qxe5", "cxd4", "Qxd4", "Qc7", "Nd2", "Bc5", "Qd3", "b6", "b4", "Bd6", "Rac1", "Bxh2+", "Kh1", "e5", "g3", "e4", "Qxd5+", "Kh8", "Kxh2", "Rf6", "Qxa8", "Rh6+", "Kg2", "1-0Black resigned • White is victorious"]

def get_fen_row(row):
    result = ''
    hyphen_counter = 0
    for square in row:
        if square == EMPTY:
            hyphen_counter += 1
        else:
            if hyphen_counter > 0:
               result += str(hyphen_counter)
               hyphen_counter = 0
            result += square
    if hyphen_counter > 0:
        result += str(hyphen_counter)
    return result

def get_board_to_fen(board):
    fen_rows = [get_fen_row(row) for row in board]
    return '/'.join(fen_rows)
    
def get_fen_notation(board, move_idx, castling_rights, misc_data):
    result = []
    board_to_fen = get_board_to_fen(board)
    result.append(board_to_fen)
    result.append(WHITE if move_idx % 2 == 1 else BLACK)
    new_castling_rights = get_castling_rights(castling_rights)
    if new_castling_rights:
        result.append(new_castling_rights)
    result.append(misc_data['en_passant_target'])
    result.append(str(misc_data['halfmove_clock']))
    result.append(str(int(move_idx // 2) + 1))
    print(' '.join(result))
    pass
    
    
for idx, move in enumerate(moves):
    print()
    print(f'{int(idx//2)+1}{"..." if idx % 2 == 1 else ""}{"   " if idx % 2 == 0 else ""}{move}')
    print('==+++++++++++==')
    print()
    process_move(board, move, WHITE if idx % 2 == 0 else BLACK, castling_rights, misc_data)
    get_fen_notation(board, idx, castling_rights, misc_data)
    print()
