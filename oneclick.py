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

def print_it(puz):
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

# go through and turn off candidates 
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

# what sudokuslam.com 'do I need a hint?' calls 'easy'
def find_single_candidates(can):
    rcis = []
    for r in range(9):
        for c in range(9):
            count=0
            which=None
            for i in range(9):
                if can[r][c][i]:
                    count += 1
                    if count > 1:
                        break
                    which = i
            if count==1:
                rcis.append( ('SINGLE', r,c,which) )
    return rcis

# a spear is a block that has all candidates in the same row
# or column, which eliminates candidates in 2 other blocks
# this is part of what sudokuslam.com calls 'little tricky'
def find_spears(can):
    spears = []
    for v in range(9):
        for br in range(3):
            for bc in range(3):
                # does block br,bc have a spear of candidate v?
                bkrows = {}
                bkcols = {}
                for rr in range(3):
                    row = br*3+rr
                    for cc in range(3):
                        col = bc*3+cc
                        if can[row][col][v]:
                            bkrows[rr] = rr
                            bkcols[cc] = cc
                if len(bkrows)==1: # it's a horizontal spear
                    bkrow = next(iter(bkrows))
                    row = br*3+bkrow
                    for obc in range(3): # throw across row other block columns
                        if obc != bc:
                            for cc in range(3):
                                if can[row][obc*3+cc][v]:
                                    spears.append( ('SPEAR', row, obc*3+cc, v) )
                if len(bkcols)==1: # it's a vertical spear
                    bkcol = next(iter(bkcols))
                    col = bc*3+bkcol
                    for obr in range(3): # throw down col to other block rows
                        if obr != br:
                            for rr in range(3):
                                if can[obr*3+rr][col][v]:
                                    spears.append( ('SPEAR', obr*3+rr, col, v) )
    return spears



def apply_moves(p, can, moves):
    for t,r,c,i in moves:
        if   t == 'SINGLE':
            p[r][c] = i        # set it
            for v in range(9): # erase all candidates
                can[r][c][v] = False
        elif t == 'SPEAR' or t == 'FORK' or t == 'SUBSET':
            can[r][c][can] = False # turn it off


if __name__ == '__main__':
    puz = SudokuGenerator(difficulty='medium').get_puzzle()

    puz = ['2..9.1583',
           '....8..7.',
           '.83.7.96.',
           '72...6.35',
           '..6835.2.',
           '...7.....',
           '64..97.5.',
           '19.3..64.',
           '3..64219.']



    #for row in puz:
    #    print(row)

    gp = gridify(puz)
    print_it(gp)

    can = all_candidates()



    #print(can)

    turn_off_candidates(gp, can)

    while True:
        onesies = find_single_candidates(can)
        if len(onesies) == 0:
            break
        apply_moves(gp, can, onesies)
        turn_off_candidates(gp, can)

    print_it(gp)






