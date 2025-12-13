import unittest

from oneclick import *

class OneClickTester(unittest.TestCase):

    def testEasy(s):
        can = all_candidates(False)

        can[0][1][2] = True
        ee = find_1_row_col_block(can)
        s.assertEqual(1, len(ee))
        eee = ee[0]
        s.assertEqual('SINGLE', eee[0])
        s.assertEqual(0, eee[1])
        s.assertEqual(1, eee[2])
        s.assertEqual(2, eee[3])

    def testSpears(s):
        # test throwing a horizontal spear
        # 111     111
        # 111 111 111
        # 111     111
        can = all_candidates(False)
        for c in range(9):
            can[4][c][1] = True
            if c < 3 or c >= 6:
                can[3][c][1] = True
                can[5][c][1] = True

        # test throwing a vertical spear
        #   2
        #   2
        #   2
        # 222
        # 222
        # 222
        # 222
        # 222
        # 222
        for r in range(9):
            can[r][8][2] = True
            if r>=3:
                can[r][6][2] = True
                can[r][7][2] = True
        ss = find_spears(can)

        s.assertEqual(12, len(ss))

    def testForks(s):
        # 333 333 333
        #         333
        # 333 333 333
        can = all_candidates(False)
        for c in range(9):
            can[6][c][3] = True
            can[8][c][3] = True
            if c>=6:
                can[7][c][3] = True

        # 44
        # 44
        # 44
        # 444
        # 444
        # 444
        # 44
        # 44
        for r in range(9):
            can[r][0][4] = True
            can[r][1][4] = True
            if r>=3 and r<6:
                can[r][2][4] = True
        ff = find_forks(can)

        s.assertEqual(12, len(ff))


    def test2subsets(s):
        can = all_candidates(False)
        # aaa 12aa a12a
        for c in range(9):
            if c==3 or c==7:
                can[0][c][1]=True
                can[0][c][2]=True
            else:
                for v in range(9):
                    can[0][c][v]=True

        ss = find_subsets_2(can)
        # remove all the 1 and 2 candidates from 7 boxes
        s.assertEqual(14, len(moves))



unittest.main()