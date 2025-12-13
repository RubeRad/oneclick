import unittest

from oneclick import *

class OneClickTester(unittest.TestCase):
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

unittest.main()