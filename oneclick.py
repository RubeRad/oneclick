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

def box_indices(arg1,arg2=None):
    if arg2 is None:
        br=arg1//3
        bc=arg1%3
    else:
        br=arg1
        bc=arg2
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


# instead of an array of 9x True/False per [r][c], have each [r][c]
# hold a set of viable candidates; hopefully will make more performant
def candisets(candidates):
    emptyrow = []
    for i in range(9):
        emptyrow.append(set())
    cs = []
    for i in range(9):
        cs.append(copy.deepcopy(emptyrow))

    for r in range(9):
        for c in range(9):
            for v in range(9):
                if candidates[r][c][v]:
                    cs[r][c].add(v)
    return cs


def find_subsets_2(can):
    moves = []

    cs = candisets(can)

    # in any row/col/block i, are there 2 cells with exactly the same 2 candidates?
    for i in range(9):
        for rcs in ( row_indices(i), col_indices(i), box_indices(i)):
            rcs2 = []
            for r,c in rcs:
                if len(cs[r][c])==2:
                    rcs2.append( (r,c) )
            if len(rcs2)<2:
                continue

            for j in range(len(rcs2)):
                rj,cj = rcs2[j]
                for k in range(j+1, len(rcs2)):
                    rk,ck = rcs2[k]
                    if cs[rj][cj] == cs[rk][ck]:
                        twoset = cs[rj][cj]
                        for r,c in rcs:
                            if r==rj and c==cj: continue
                            if r==rk and c==ck: continue
                            for v in twoset:
                                if can[r][c][v]:
                                    moves.append( ('2SET', r, c, v) )

    return  moves

def find_subsets_3(can):
    moves = []
    cs = candisets(can)
    # in any row/col/block idx, are there 3 cells with the same 3 candidates?
    for idx in range(9):
        for rcs in ( row_indices(idx), col_indices(idx), box_indices(idx) ):
            rcs3 = []
            for r,c in rcs:
                if len(cs[r][c])==2 or len(cs[r][c])==3:
                    rcs3.append( (r,c) )
            if len(rcs3)<3:
                continue

            for i in range(len(rcs3)):
                ri,ci = rcs3[i]
                for j in range(i+1,len(rcs3)):
                    rj,cj = rcs3[j]
                    uu = cs[ri][ci].union(cs[rj][cj])
                    if len(uu)>3:
                        continue
                    for k in range(j+1,len(rcs3)):
                        rk,ck = rcs3[k]
                        uuu = uu.union(cs[rk][ck])
                        if len(uuu) == 3:
                            for r,c in rcs:
                                if r==ri and c==ci: continue
                                if r==rj and c==cj: continue
                                if r==rk and c==ck: continue
                                for v in uuu:
                                    if can[r][c][v]:
                                        moves.append( ('3SET', r, c, v) )
    return moves

def find_moves(can):
    moves = find_1_row_col_block(can)
    moves.extend( find_spears(can) )
    moves.extend( find_forks(can) )
    moves.extend( find_subsets_2(can) )
    moves.extend( find_subsets_3(can) )
    return moves


def apply_move(puz, can, mov):
    t,r,c,i = mov
    if   t == 'SINGLE':
        puz[r][c] = i      # set it into the puzzle
        for v in range(9): # erase all candidates
            can[r][c][v] = False
    elif t == 'SPEAR' or t == 'FORK' or t == '2SET' or t == '3SET':
        can[r][c][i] = False # turn it off


if __name__ == '__main__':
  founit = False
  while not founit:
    puzl = SudokuGenerator(difficulty='hard').get_puzzle()

    # sudokuslam.com medium puzzle mid-solve
    # involves 'hard' (both 2SET and 3SET moves)
    if False:
        # sudokuslam.com medium puzzle involving 2SET/3SET moves
        # mid-solve
        puzl = ['2.......9',
                '.89.....6',
                '.3...5.41',
                '.4.783192',
                '.1.529468',
                '892416753',
                '.....261.',
                '......9.7',
                '.....13..']
        puzl = ['2........',
                '.89......',
                '.3...5.41',
                '.4.7.3..2',
                '.1.5.....',
                '89.4...5.',
                '.....261.',
                '......9.7',
                '.....13..']


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
                copy_puz = copy.deepcopy(sudoku)
                copy_can = copy.deepcopy(candidates)

            apply_move(sudoku, candidates, moves[0])

            cascade(sudoku, candidates)
            if done(sudoku):
                if onemove:
                    print('Single move triggered winning cascade!')
                    founit=True
                print('All done!')
                print_puzzle(sudoku)
                break

  print("Here's what I found:")
  print_puzzle(copy_puz)
  print_candidates(copy_can)