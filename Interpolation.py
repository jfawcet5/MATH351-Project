def difTable(X, Y):
    """
    Creates a divided difference table for a list of x and y coordinates.
    """
    n = len(Y)
    table = [[0] * n for i in range(n)]
    
    for i in range(n):
        table[i][0] = Y[i]

    for j in range(1, n):
        for i in range(0, n-j):
            table[i][j] = (table[i+1][j-1] - table[i][j-1]) / (X[i+j] - X[i])
    return table

def printTable(table):
    '''
    Function to print the divided difference table.
    '''
    print("Divided Difference Table: ")
    for val in table:
        print('\t'.join(map(str, val)))
    print()
    
def newtonsIP(X, Y, x):
    '''
    Function for Newton Interpolation, which takes in
    a list of x coordinates, a list of y coordinates,
    and a x value where the resulting polynomial will
    be evaluated at.
    '''
    n = len(Y) - 1
    table = difTable(X, Y)

    #printTable(table)
    
    result = table[0][n]
    for i in range(1, n+1):
        result = table[0][n-i] + (x - X[n-i])* result
    return result

def main():
    '''
    Sample run of Newton's Interpolation
    '''
    x_coords = [0, 0.5, 1, 2]
    y_coords = [1, 2, 0, -1]
    eval_x = 9
    
    result = newtonsIP(x_coords, y_coords, eval_x)
    print(f"result of interpolated polynomial at x = {eval_x} is {result}")

if __name__ == "__main__":
    main()
    
