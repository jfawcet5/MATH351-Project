""" This file implements the Newton's Interpolation functionality.

    Authors: Joshua Fawcett, Hans Prieto
"""

def newtonsIP(Xs, Ys):
    '''
    Creates a divided difference table for a list of x and y coordinates.
    '''
    n = len(Ys)
    table = [[0] * n for i in range(n)]
    
    for i in range(n):
        table[i][0] = Ys[i]

    for j in range(1, n):
        for i in range(0, n-j):
            table[i][j] = (table[i+1][j-1] - table[i][j-1]) / (Xs[i+j] - Xs[i])
    return table

def evaluatePolynomial(x, Xs, table):
    '''
    Evaluates the polynomial at a given x coordinate by using a list of X coordinates
    and a divided difference table.
    '''
    n = len(Xs) - 1
    result = table[0][n]
    for i in range(1, n+1):
        result = table[0][n-i] + (x - Xs[n-i])* result
    return result
    
def printTable(table):
    '''
    Function to print the divided difference table.
    '''
    print("Divided Difference Table: ")
    for val in table:
        print('\t'.join(map(str, val)))
    print()

def main():
    '''
    Sample run of Newton's Interpolation
    '''
    x_coords = [0, 0.5, 1, 2]
    y_coords = [1, 2, 0, -1]
    eval_x = 9

    # Create the divided difference table for the polynomial given x_coords and y_coords
    difTable = newtonsIP(x_coords, y_coords)

    # Print the divided difference table
    printTable(difTable)

    # Evaluate the polynomial at given x coordinate(eval_x) by using list of x coordinates
    # (x_coords) and the divided difference table for the polynomial(difTable)
    result = evaluatePolynomial(eval_x, x_coords, difTable)

    # Print the result
    print(f"Result of interpolated polynomial at x = {eval_x} is {result}")

if __name__ == "__main__":
    main()
    
