import ast
import re
import math
from scipy.optimize import linprog
import numpy as np
import sys



# Regex to check if input is valid as a constraint.
def isValidCon(constraint):
    try:
        a = (re.search(r"\[\-?\s*[0-9]+\s*(\,\s*\-?\s*[0-9]+\s*)*\]\s*x?\s*[<>=]\=\s*\-?\s*[0-9]+", constraint)).group(0)
        return True
    except AttributeError:
        return False

# Regex to check if input is valid as objective value.
def isValidObj(obj):
    try:
        (re.search(r"^\[(\-?\s*[0-9]+(\,\s*\-?\s*[0-9]+)*)\]$", obj)).group(0)
        return True
    except AttributeError:
        return False


# Main input/output function. 
def interface():
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

    count = 0
    constraints = []
    while True:
        print("Please enter your next constraint. For example, '[4,3,2]x <= 15' and '[1,2,3]x == 1' are valid constraints.")
        newcon = raw_input("Type 'end' when finished. ")
        if newcon == 'end':
            break
        if isValidCon(newcon):
            constraints.append(newcon)
            count += 1
        else:
            print("There was an error. Please enter a valid constraint.")
    A = []
    Aeq = []
    b = []
    beq = []
    for con in constraints:
        newRow = ast.literal_eval(re.search(r'\[.*\]', con).group(0))
        inequality = re.search(r'[<>=]\=', con).group(0)
        newB = float(re.split('[<=>]\=\s*', con)[1])
        if inequality == '<=':
            A.append(newRow)
            b.append(newB)
        elif inequality == '==':
            Aeq.append(newRow)
            beq.append(newB)
        elif inequality == '>=':
            A.append([x * -1 for x in newRow])
            b.append(-1*newB)
    if direction == 'min':
        if problem == 'linear':
            bestX = linearPro(c, A, b, Aeq, beq)
            print sum([x*y for x,y in zip(c, bestX)])
        else:
            print integerPro(c, A, b, Aeq, beq)
    else:
        newAeq = [list(i) for i in zip(*(A + Aeq))]
        newbeq = c 
        newC = b + beq
        if problem == 'linear':
            bestX = linearPro(newC, None, None, newAeq, newbeq)
            print sum([x*y for x,y in zip(c, bestX)])
        else:
            print integerPro(newC, None, None, newAeq, newbeq)






# Ax <= b
def linearPro(c, A, b, Aeq, beq):
    if not A:
        res = linprog(c, A_eq=Aeq, b_eq=beq, options={"disp":False})
    else:
        res = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, options={"disp":False})
    if (type(res.x) is float): #produces error code
        return 'infeasible'
    else:
        return res.x


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




