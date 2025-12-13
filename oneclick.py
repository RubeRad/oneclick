#! bin/python

import copy

from sudoku9 import SudokuGenerator


def gridify(stringpuz):
    gpuz = []
    for row in stringpuz:
        ary = []
        for c in row:
            if c == '.':
                ary.append(None)
            else:
                ary.append(int(c)-1) # 1-9 --> 0-8
        gpuz.append(ary)
    return gpuz

def print_puzzle(puz):
    for ri in range(9):
        for ci in range(9):
            v = puz[ri][ci]
            if v is None:
                print('.', end='')
            else:
                print(v, end='')
            if ci%3==2:
                print(' ', end='')
        print('')
        if ri%3==2:
            print('')

def print_candidates(can):
    for r in range(9):
        for rr in range(3):
            for c in range(9):
                for cc in range(3):
                    v = rr*3+cc
                    if can[r][c][v]: print(v,   end='')
                    else:            print(' ', end='')
                print('|', end='')
            print('')
        print('------------------------------------')



def all_candidates(val=True):
    # fill in all candidates as 1 to start
    true9 = []
    for i in range(9):
        true9.append(val)
    true99 = []
    for i in range(9):
        true99.append(copy.deepcopy(true9))
    true999 = []
    for i in range(9):
        true999.append(copy.deepcopy(true99))
    return true999

# return 2-tuples for all the elements in a row/col/box
def row_indices(r):
    rcs = []
    for c in range(9):
        rcs.append( (r,c) )
    return(rcs)

def col_indices(c):
    rcs = []
    for r in range(9):
        rcs.append( (r,c) )
    return(rcs)

def box_indices(br,bc):
    rcs = []
    for r in range(3):
        for c in range(3):
            rcs.append( (br*3+r, bc*3+c) )
    return(rcs)

# go through and turn off candidates based on values that are set
# sudokuslam.com 'sumo mode'
def turn_off_candidates(puz,can, verbose=False):
    didsumpn = False
    for r in range(9):
        for c in range(9):
            vrc = puz[r][c]
            if vrc is None:
                continue

            # r,c is filled in, turn off all candidates
            for i in range(9):
                if can[r][c][i]:
                    didsumpn = True
                    can[r][c][i] = False

            rowis = row_indices(r)
            for rr,cc in rowis:
                if can[rr][cc][vrc]:
                    didsumpn = True
                    can[rr][cc][vrc] = False
                    if verbose:
                        print(f'{r},{c} is {vrc} so row-off {rr},{cc}')

            colis = col_indices(c)
            for rr,cc in colis:
                if can[rr][cc][vrc]:
                    didsumpn = True
                    can[rr][cc][vrc] = False
                    if verbose:
                        print(f'{r},{c} is {vrc} so col-off {rr},{cc}')

            boxis = box_indices(r//3, c//3)
            for rr,cc in boxis:
                if can[rr][cc][vrc]:
                    didsumpn = True
                    can[rr][cc][vrc] = False
                    if verbose:
                        print(f'{r},{c} is {vrc} so box-off {rr},{cc}')

    return didsumpn

# sudokuslam.com 'autofill obvious numbers'
def autofill(puz, can):
    didsumpn = False
    for r in range(9):
        for c in range(9):
            vset = set()
            for v in range(9):
                if can[r][c][v]:
                    vset.add(v)
                    if len(vset)>1:
                        break # 2+ candidates for this [r][c]
            if len(vset)==1:
                puz[r][c] = vset.pop()
                for vv in range(9):
                    can[r][c][v] = False
                didsumpn = True
    return didsumpn

def cascade(puz,can):
    while turn_off_candidates(puz,can) or autofill(puz,can):
        pass

def done(puz):
    for r in range(9):
        for c in range(9):
            if puz[r][c] is None:
                return False
    return True

# what sudokuslam.com 'do I need a hint?' calls 'easy'
def find_1_row_col_block(can):
    # put these in a set because they might duplicate
    # like if a candidates grid has a single True at can[1][2][3]==True
    # that's a SINGLE for row 1, and col 2, and block 0
    easyset = set()
    for val in range(9):
        for i in range(9): # check all the things
            # is there a row such that only one square has candidate val?
            row = i
            cset = set()
            for col in range(9):
                if can[row][col][val]:
                    cset.add(col)
                if len(cset)>1:
                    break
            if len(cset)==1: # yup!
                easyset.add( ('SINGLE', row, cset.pop(), val) )

            # is there a col such that only one square has candidate val?
            col = i
            rset = set()
            for row in range(9):
                if can[row][col][val]:
                    rset.add(row)
                if len(rset)>1:
                    break
            if len(rset)==1: # yup!
                easyset.add( ('SINGLE', rset.pop(), col, val) )

            # is there a block such that only one square has candidate val?
            br = i//3
            bc = i%3
            bset = set()
            for ii in range(9):
                row = br*3+ii//3
                col = bc*3+ii%3
                if can[row][row][val]:
                    bset.add( (row,col) )
                    if len(bset)>1:
                        break
            if len(bset)==1: # yup!
                row,col = bset.pop()
                easyset.add( ('SINGLE', row, col, val) )

    # convert out to a list
    return list(easyset)


# a spear is a block that has all candidates in the same row
# or column, which eliminates candidates in 2 other blocks
# this is part of what sudokuslam.com calls 'little tricky'
def find_spears(can):
    spears = []
    for v in range(9):
        for br in range(3):
            for bc in range(3):
                # does block br,bc have a spear of candidate v?
                bkrows = set()
                bkcols = set()
                for rr in range(3):
                    row = br*3+rr
                    for cc in range(3):
                        col = bc*3+cc
                        if can[row][col][v]:
                            bkrows.add(rr)
                            bkcols.add(cc)
                if len(bkrows)==1: # it's a horizontal spear
                    row = br*3+bkrows.pop()
                    for obc in range(3): # throw across row other block columns
                        if obc != bc:
                            for cc in range(3):
                                if can[row][obc*3+cc][v]:
                                    spears.append( ('SPEAR', row, obc*3+cc, v) )
                if len(bkcols)==1: # it's a vertical spear
                    col = bc*3+bkcols.pop()
                    for obr in range(3): # throw down col to other block rows
                        if obr != br:
                            for rr in range(3):
                                if can[obr*3+rr][col][v]:
                                    spears.append( ('SPEAR', obr*3+rr, col, v) )
    return spears

# A fork is when two blocks in the same row(col) have candidates all in the same
# two rows(cols), which eliminates candidates in those rows(cols) in the third
# block. the other part of sudokuslam.com 'little tricky'
def find_forks(can):
    forks = []
    for v in range(9):
        #print('v', v)
        for nbi in range(3): # which block is NOT part of the fork?
            bi0 = 1 if nbi==0 else 0 # bi0 will be 0 unless nbi pushes it up to 1
            bi1 = 1 if nbi==2 else 2 # bi0 will be 2 unless nbi pushes it dn to 1
            bfk = 3-(bi0+bi1) # block that is forked
            #print('nbi', nbi, bi0, bi1, bfk)
            for oi in range(3): # other block index
                #print('oi',oi)
                # does row oi have a fork in cols bi0,bi1 against block bfk?
                # Where are all the candidates in the two blocks?
                bkrows0 = set()
                bkrows1 = set()
                for rr in range(3):
                    row = oi*3+rr
                    for cc in range(3):
                        col0 = bi0*3+cc
                        col1 = bi1*3+cc
                        if can[row][col0][v]:
                            bkrows0.add(rr)
                        if can[row][col1][v]:
                            bkrows1.add(rr)
                if len(bkrows0)==2 and len(bkrows1)==2 and bkrows0==bkrows1:
                    # it's a fork! stab the block in column bfk
                    rr0 = bkrows0.pop()
                    rr1 = bkrows0.pop()
                    for cc in range(3):
                        col = bfk*3+cc
                        row = oi*3+rr0
                        if can[row][col][v]:
                            forks.append( ('FORK', row, col, v) )
                        row = oi*3+rr1
                        if can[row][col][v]:
                            forks.append( ('FORK', row, col, v) )

                # does col oi have a fork in cols bi0bi1 against block bfk?
                # Where are all the candidates in the two blocks?
                bkcols0 = set()
                bkcols1 = set()
                for cc in range(3):
                    col = oi * 3 + cc
                    for rr in range(3):
                        row0 = bi0 * 3 + rr
                        row1 = bi1 * 3 + rr
                        if can[row0][col][v]:
                            bkcols0.add(cc)
                        if can[row1][col][v]:
                            bkcols1.add(cc)
                if len(bkcols0) == 2 and len(bkcols1) == 2 and bkcols0 == bkcols1:
                    # it's a fork! stab the block in row bfk
                    cc0 = bkcols0.pop()
                    cc1 = bkcols0.pop()
                    for rr in range(3):
                        row = bfk * 3 + rr
                        col = oi * 3 + cc0
                        if can[row][col][v]:
                            forks.append(('FORK', row, col, v))
                        col = oi * 3 + cc1
                        if can[row][col][v]:
                            forks.append(('FORK', row, col, v))
    return forks


def find_moves(can):
    moves = find_1_row_col_block(can)
    moves.extend( find_spears(can) )
    moves.extend( find_forks(can) )
    return moves


def apply_move(puz, can, mov):
    t,r,c,i = mov
    if   t == 'SINGLE':
        puz[r][c] = i      # set it into the puzzle
        for v in range(9): # erase all candidates
            can[r][c][v] = False
    elif t == 'SPEAR' or t == 'FORK' or t == 'SUBSET':
        can[r][c][i] = False # turn it off


if __name__ == '__main__':
    puzl = SudokuGenerator(difficulty='hard').get_puzzle()

    #puz = ['2..9.1583',
    #       '....8..7.',
    #       '.83.7.96.',
    #       '72...6.35',
    #       '..6835.2.',
    #       '...7.....',
    #       '64..97.5.',
    #       '19.3..64.',
    #       '3..64219.']

    #for row in puz:
    #    print(row)

    sudoku = gridify(puzl)
    print_puzzle(sudoku)
    candidates = all_candidates()
    turn_off_candidates(sudoku, candidates)
    print_candidates(candidates)
    cascade(sudoku, candidates)
    if done(sudoku):
        print('All done!')
        print_puzzle(sudoku)

    else:
        # solution loop
        while True:
            moves = find_moves(candidates)
            nmoves = len(moves)
            if nmoves==0:
                print("can't find any moves")
                print_puzzle(sudoku)
                print_candidates(candidates)
                break

            print(f'there are {nmoves} available, first is {moves[0]}')
            onemove = (nmoves==1)
            if onemove:
                print("There is just one move!")
                print_puzzle(sudoku)
                print_candidates(candidates)
            apply_move(sudoku, candidates, moves[0])

            cascade(sudoku, candidates)
            if done(sudoku):
                if onemove:
                    print('Single move triggered winning cascade!')
                print('All done!')
                print_puzzle(sudoku)
                break