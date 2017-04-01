from src import utils
import unittest

class TestCases(unittest.TestCase):

    def test_get_weak_option(self):
        permutation_k = ['0','1','2']
        weak_j = utils.get_weak_option(permutation_k=permutation_k,option_j='1')
        self.assertEqual(['2'], weak_j)

    def test_get_weak_option_2(self):
        permutation_k = ['0','1','2','3','4']
        weak_j = utils.get_weak_option(permutation_k=permutation_k,option_j='1')
        self.assertEqual(['2','3','4'], weak_j)


if __name__ == '__main__':
    unittest.main()