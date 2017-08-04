import ast
import re
import math
from scipy.optimize import linprog
import numpy as np
import sys



# isValidCon takes a string and checks to see if it is a valid constraint. 
def isValidCon(constraint):
    try:
        a = (re.search(r"\[\-?\s*[0-9]+\s*(\,\s*\-?\s*[0-9]+\s*)*\]\s*x?\s*[<>=]\=\s*\-?\s*[0-9]+", constraint)).group(0)
        return True
    except AttributeError:
        return False

# Similar to isValidCon, but checks to see if input string is a valid objective function
def isValidObj(obj):
    try:
        (re.search(r"^\[(\-?\s*[0-9]+(\,\s*\-?\s*[0-9]+)*)\]$", obj)).group(0)
        return True
    except AttributeError:
        return False


# Main input/output function. 
def interface():
    # First collect inputs
    while True:
        problem = raw_input("Is this a linear or integer programming problem? (linear/integer) ").lower()
        if (problem == 'linear' or problem == 'integer'):
            break
        else:
            print("Please enter a valid response.")

    while True:
        direction = raw_input("Are you maximizing or minimizing your objective? (max/min) ").lower()
        if (direction == 'max' or direction == 'min'):
            break
        else:
            print("Please enter a valid response.")

    while True:
        tmp = raw_input("Please enter your objective function. For example, '[4,2,3]' would mean 4*x1 + 2*x2 + 3*x3. ")
        if not isValidObj(tmp):
            print("Please enter a valid response.")
        else:
            c = np.asarray(ast.literal_eval(tmp))
            break
    constraints = []
    while True:
        print("Please enter your next constraint. For example, '[4,3,2]x <= 15' and '[1,2,3]x == 1' are valid constraints.")
        newcon = raw_input("Type 'end' when finished. ")
        if newcon == 'end':
            break
        if isValidCon(newcon):
            constraints.append(newcon)
        else:
            print("There was an error. Please enter a valid constraint.")

    """
    We initialize are matrices/vectors to perform linear programming
    Our problem looks like the following:

    min/max c * x
    subject to:
        Ax_1 <= b
        Aeqx_2 <= beq
    where x_1 and x_2 are vectors.
    """
    A = []
    Aeq = []
    b = []
    beq = []
    for con in constraints: # For each constraint, we split our right hand and left hand into A and b respectively. 
        newRow = ast.literal_eval(re.search(r'\[.*\]', con).group(0))
        inequality = re.search(r'[<>=]\=', con).group(0)
        newB = float(re.split('[<=>]\=\s*', con)[1])
        if inequality == '<=':
            A.append(newRow)
            b.append(newB)
        elif inequality == '==':
            Aeq.append(newRow)
            beq.append(newB)
        elif inequality == '>=': # Since scipy.optimize only allows <=, we have to flip our inequality to fit.
            A.append([x * -1 for x in newRow])
            b.append(-1*newB)
    if direction == 'min':
        if problem == 'linear':
            bestX = linearPro(c, A, b, Aeq, beq) # returns the best x value that we get
            print sum([x*y for x,y in zip(c, bestX)])
        else:
            print integerPro(c, A, b, Aeq, beq)
    else:
        """
        scipy.optimize only minimizes linear programs, so we have to find the dual of our problem to change our maximization problem into a minimization
         The dual will become the following:
            min b*y
            subject to:
            A^T*y == c
        where A^T is A transposed.
        See more about duality on wikipedia.
        """
        newAeq = [list(i) for i in zip(*(A + Aeq))]
        newbeq = c 
        newC = b + beq
        if problem == 'linear':
            bestX = linearPro(newC, None, None, newAeq, newbeq) # Returns our optimal X vector
            print sum([x*y for x,y in zip(c, bestX)]) # Returns our optimal value solution
        else:
            print integerPro(newC, None, None, newAeq, newbeq)






# Simply calls scipy.optimize.linprog
# Returns the optimal x vector
def linearPro(c, A, b, Aeq, beq):
    if not A:
        res = linprog(c, A_eq=Aeq, b_eq=beq, options={"disp":False})
    else:
        res = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, options={"disp":False})
    if (type(res.x) is float): #produces error code
        return 'infeasible'
    else:
        return res.x

# Performs branch-and-bound to derive an integer solution for x.
# Returns the optimal x vector that contain all integer values
def integerPro(c, A, b, Aeq, beq):
    bestX = linearPro(c, A, b, Aeq, beq)
    if type(bestX) is str:
        return [sys.maxint, bestX]
    bestVal = sum([x*y for x,y in zip(c, bestX)])
    if all(item.is_integer() for item in bestX):
        return bestVal
    else:
        ind = [i for i, x in enumerate(bestX) if type(x) is not int][0]
        newCon = [0] * len(A[0])
        newCon[ind] = 1
        newA = A.append(newCon)
        newB1 = b.append(math.ceil(bestX[ind]))
        newB2 = b.append(math.floor(bestX[ind]))
        return min(integerPro(c, newA, newB1, Aeq, beq), integerPro(c, newA, newB2, Aeq, beq))



interface()




