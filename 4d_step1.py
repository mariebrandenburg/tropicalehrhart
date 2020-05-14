import sys
import numpy as np
from sage.all import *
output_file = open("out/erhart_tests_1_9999","w")
for line in sys.stdin:

    input_data = line.rstrip()
    input_data = input_data[1:len(input_data)-1].split('[')
    data_as_strings = []
    for vec in input_data:
        if len(vec):
            data_as_strings.append(vec[:vec.index(']')])

    #extract fractions and convert to lists representing rational numbers
    denominators = []
    data_rat = []
    for string in data_as_strings:
        string = string.split(',')
        numbers = []
        for number in string[1:]:
            if '/' in number:
                numerator = int(number[:number.index('/')].strip())
                denominator = int(number[number.index('/')+1:].strip())
                denominators.append(denominator)
                numbers.append([numerator,denominator])
            else:
                numbers.append([int(number)])
        data_rat.append(numbers)


    multiple = np.lcm.reduce(denominators)
    data_int = []

    #convert to integer matrix
    for vec in data_rat:
        vector_int = []
        for rat_number in vec:
            if len(rat_number)==1:
                vector_int.append(rat_number[0]*multiple)
            else:
                vector_int.append(rat_number[0]*multiple/rat_number[1])
        data_int.append(vector_int)

    #compute Kleene star
    P = Polyhedron(vertices=data_int, backend='normaliz', base_ring=QQ)
    #P = Polyhedron(vertices=data_int)
    var('x1,x2,x3,x4,x5')
    variables = vector([x1,x2,x3,x4,x5])
    p = MixedIntegerLinearProgram()
    v = p.new_variable(real=True)
    x1,x2,x3,x4,x5 = v['x1'], v['x2'], v['x3'], v['x4'], v['x5']
    for line in P.Hrepresentation():
        if line.is_inequality():
            p.add_constraint(eval(str(line.A()*variables)+"+("+str(line.b())+")>=0"))
        elif line.is_equation():
            p.add_constraint(eval(str(line.A()*variables)+"+("+str(line.b())+")==0"))

    e = [vector([1,0,0,0,0]), vector([0,1,0,0,0]), vector([0,0,1,0,0]), vector([0,0,0,1,0]), vector([0,0,0,0,1])]
    indices = [(i,j) for i in range(5) for j in range(5) if not i==j]
    kleene = [[0]*5 for i in range(5)]
    for (i,j) in indices:
        objective = e[i] - e[j]
        p.set_objective(eval(str(objective*variables)))
        kleene[i][j] = int(p.solve())

    w = str([kleene[i][j] for i in range(len(kleene)) for j in range(len(kleene[0])) if not i==j])
    vertex = P.vertices()[0].vector()
    min_prime = '*'.join(['x'+str(i+1)+str(j+1) for (i,j) in indices if vertex[i]-vertex[j]==kleene[i][j]])

    output = '{'+str(w[1:len(w)-1])+'}; '+min_prime
    print(output)
    output_file.write(str(P.ehrhart_polynomial())+'\n')