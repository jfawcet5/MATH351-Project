""" This file tests the Newton's Interpolation functionality, given a certain number of points.

    Authors: Joshua Fawcett, Hans Prieto
"""

import Interpolation
import unittest

class test_interpolation(unittest.TestCase):
    def test_one_point(self):
        '''
        Tests Newton's Interpolation with one point.
        '''
        x_coord = [0]
        y_coord = [1]
        eval_x = 9

        # compute divided difference table
        difTable = Interpolation.newtonsIP(x_coord, y_coord)
        actual_table = [[1]]

        # compare computed divided difference table with actual table
        self.assertEqual(difTable, actual_table)
        
        #compute result
        computed_result = Interpolation.evaluatePolynomial(eval_x, x_coord, difTable)
        actual_result = 1
        
        # compare computed result with actual result
        self.assertEqual(computed_result, actual_result)

    def test_two_points(self):
        '''
        Tests Newton's Interpolation with two points.
        '''
        x_coords = [0, 0.5]
        y_coords = [1, 2]
        eval_x = 9

        # compute divided difference table
        difTable = Interpolation.newtonsIP(x_coords, y_coords)
        actual_table = [[1, 2],
                        [2, 0]]

        # compare computed divided difference table with actual table
        self.assertEqual(difTable, actual_table)
        
        #compute result
        computed_result = Interpolation.evaluatePolynomial(eval_x, x_coords, difTable)
        actual_result = 19

        # compare computed result with actual result
        self.assertEqual(computed_result, actual_result)

    def test_three_points(self):
        '''
        Tests Newton's Interpolation with three points.
        '''
        x_coords = [0, 0.5, 1]
        y_coords = [1, 2, 0]
        eval_x = 9

        # compute divided difference table
        difTable = Interpolation.newtonsIP(x_coords, y_coords)
        actual_table = [[1, 2, -6],
                        [2, -4, 0],
                        [0, 0, 0]]

        # compare computed divided difference table with actual table
        self.assertEqual(difTable, actual_table)
        
        #compute result
        computed_result = Interpolation.evaluatePolynomial(eval_x, x_coords, difTable)
        actual_result = -440

        # compare computed result with actual result
        self.assertEqual(computed_result, actual_result)

    def test_four_points(self):
        '''
        Tests Newton's Interpolation with four points.
        '''
        x_coords = [0, 0.5, 1, 2]
        y_coords = [1, 2, 0, -1]
        eval_x = 9
        
        # compute divided difference table
        difTable = Interpolation.newtonsIP(x_coords, y_coords)
        actual_table = [[1, 2, -6, 4],
                        [2, -4, 2, 0],
                        [0, -1, 0, 0],
                        [-1, 0, 0, 0]]

        # compare computed divided difference table with actual table
        self.assertEqual(difTable, actual_table)

        #compute result
        computed_result = Interpolation.evaluatePolynomial(eval_x, x_coords, difTable)
        actual_result = 2008

        # compare computed result with actual result
        self.assertEqual(computed_result, actual_result)

if __name__ == '__main__':
    unittest.main()
