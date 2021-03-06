"""
LED evaluator
Dr. Nelson Rushton, Texas Tech University
July, 2014

##########################################
Definitions

An *Expression* is one of the following

  1. a number
  2. A pair (F,X) where F is an operator and X is a list of expressions.

An *LED data* is a rational number, an atom, a truth value, a vector of data, a finite set of data, a tuple of data 

In this program, the variable E will vary over Expression's.
The top function of this file is val

##########################################
Error handling in the evaluator

The function signature of val is Expression -> LED data or Experssion -> str
If E is an expression and all the operations in E are valid, val(E)=V, where v is the value of E.
If E is an expression and one of the operations in E is not valid, val(E) = message, where message is a string indicating which operation is not valid.

All the functions that are called within val should return the same format of the result as val, which is LED data * str.
##########################################

"""
from LED.Expression import *
from LED.LEDProgram import Program
from LED.LEDProgram import TypeChecking
from _functools import reduce
from fractions import Fraction
#@profile
def val(E):
    #print(E)
    #print(dictionary.length()
    if dictionary.hasKey(E):
        #print("retrieving E in dictionary",E)
        return dictionary.valueOf(E)
    if E==None:
        return
    # if E is an expression
    # for performance purpose, check if is tuple first to prevent further checking
    if not isinstance(E,tuple):
        if isScalar(E) or isBuiltInType(E):
            # for some reason, if E==1, dictionary[E]=E would store True but not 1
            # in python, True and 1 are interchangeble 
            if E==1:
                dictionary.update(E,1)
                #dictionary[E]=1
            else:
                dictionary.update(E,E)
                #dictionary[E]=E
            return E
    if isinstance(E,str) and Program.defined(E,0) :  
        #return valDefined(E,[])
        value = valDefined(E,[])
        if not value==None:
            #dictionary.update(E,value)
            return value
        print('Error in evaluating call',str(E)+'()')
        return
   
    if isinstance(E,str) and not Program.defined(E,0): 
        print("0-ary function",E,"is not defined") 
        return
    (Op,X) = E
    X=tuple(X)
    if Op in {'and','<=>','=>','some','all','setComp','Union','Sum','Prod','Nrsec','lambda'}: Args=X
    else: 
        #print(E)
        Args = [val(E) for E in X]
        Args = tuple(Args)
    # return None if one of the arguments is None
    if hasNone(Args): 
        #print('One of the arguments is not valid')
        return 

    if Op in ['seq','set','tuple','star','comStar','lambda','fSet','Seq','string']: 
        # use frozenset instead of list to store set 
        if Op=='set':
            Args = frozenset(Args)
        else:
            Args = tuple(Args)
        dictionary.update((Op,Args),(Op,Args))
        #dictionary[(Op,Args)]=(Op,Arg
        return (Op,Args)
    if Op in builtIns : 
        # check if Op is one of the Big Operations
        #if Op in ['setComp','Union','Sum','Prod','Nrsec']:
        try:
            if dictionary.hasKey((Op,Args)):
                value = dictionary.valueOf((Op,Args))
            else:
                value = valBuiltIn(Op,Args)
                dictionary.update((Op,Args),value)
            return value
        except:
            print('Operation',Op,'not valid on arguments:',prettyArgs(Args))    
            return
    if Program.defined(Op,len(Args)): 
    #return  valDefined(Op,Args)
        value = valDefined(Op,Args)
        if not value == None:
            #dictionary[Op,X]=value
            dictionary.update((Op,Args),value)
            #dictionary[Op,Args]=value
            return value
        print('Error in evaluating call',str(Op)+'('+prettyStack(Args)+')')       
        return
    
    if not Program.defined(Op,len(Args)): 
        print(str(len(Args))+"-ary function",Op,"is not defined") 
        return

# If Args is a list of values. hasNone(Args) is True iff there is at least one element in Args whose value is None.
def hasNone(Args):
    if Args == None:
        return True
    for arg in Args:
        if arg==None:
            return True
    return False
def valBuiltIn(Op,Args):
    # deal with type Union
    if Op=='U' and not all([x[0]=='set' for x in Args]):
        return (Op,Args)
    F = builtIns[Op]
    return F(Args)
#@profile
def valDefined(Op,Args): 
    # Op is the name of user defined function
    (params,funBody,guardCon,signature) = Program.body(Op,len(Args))
    funBodyExpression = funBody.expression()
    # substitute for all the instances of paramters in the function definition
    guardConExpr = guardCon.expression()
    subGuardConExpr = subAll(Args,params,guardConExpr)     # find the solution set of the guard condition
    binding = solutionSet(subGuardConExpr)
    if binding==None or len(binding)==0:
        print('Erroneous call',Op,'.Guard condition of function',Op,'is not meet.')
        return
    else:
        expr=subExpression(funBodyExpression,binding[0])
    # check to see if the expr belows to input of the function signature
    e =(tuple(Args),tuple(params),expr)
    #if e in dictionary:
    if dictionary.hasKey(e):
        groundBody = dictionary.valueOf(e)
    else:
        groundBody = subAll(Args,params,expr)
        dictionary.update(e,groundBody)
        #dictionary[e]=groundBody
    if isinstance(Args,tuple):
        if len(Args)>1:
            Args = ('tuple',tuple(Args))
        #if len(Args)==1 and len(Args[0])>1:
        #    Args = ('tuple',Args[0])
        if len(Args)==1:
            Args = Args[0]

    if signature!=None and TypeChecking.flag:
        if not valMember([Args,val(signature[0].expression())]):
            print('The input of the function:',Args,'does not comply with type',signature[0],'in the function signature')
            return
        value=DefVal(groundBody)
        if not valMember([value,val(signature[1].expression())]):
            print('The output of the function:', value,'does not comply with the type',signature[1],' in the function signature')
            #return
    if dictionary.hasKey(groundBody):
        value = dictionary.valueOf(groundBody)
    else:
        value=DefVal(groundBody)
        dictionary.update(groundBody,value)
    value=DefVal(groundBody)
    return value

def DefVal(fbody):
    #print(fbody)
    if not isinstance(fbody,tuple):
        # function body is a user defined constant
        if Program.defined(fbody,0):
            return val(fbody)
        return fbody
    if not fbody[0] == 'cond' :
        return val(fbody)
    # function body is a conditional
    for clause in fbody[1]:
        (op,Args) = clause
        Args=tuple(Args)
        if op == 'if':
            [guard,term] = Args
            guardValue = val(guard)
            if guardValue: return val(term)
        if op == 'ow':
            term = Args[0]
            return val(term)

def subAll(Vals,Vars,E):
    a = E
    for i in range(len(Vals)):
        exp = (Vals[i],Vars[i],a)
        if dictionary.hasKey(exp):
            a= dictionary.valueOf(exp)
        else:
            a = sub(Vals[i],Vars[i],a)
            dictionary.update(exp,a)
            #dictionary[exp]=a
        #a = sub(Vals[i],Vars[i],a)
    return a

def sub(c,x,T):
    if T==None:
        return
    e=(c,x,T)
    if dictionary.hasKey(e):
        return dictionary.valueOf(e)
    if isScalar(T): 
        return T
    elif T==x:  
        return c
    elif isinstance(T, str): return T
    (Op,Args) = T
    val = ((sub(c,x,Op),tuple([sub(c,x,A) for A in Args])))
    dictionary.update(e,val)
    #dictionary[e]=val
    return val

# Each built-in operator is evaluated by a separate function.
# These functions assume argument X has been evaluated, except
# valNonStrictAnd and valNonStrictImplies.

# Arithmetic ops                   
def valAdd(X): 
    return X[0]+X[1]
def valSubtract(X): return X[0]-X[1]
def valMult(X): return X[0]*X[1]
def valDiv(X): 
    if X[1]==0:
        print('error: division by zero')
        return
    else:
        return Fraction(X[0]) / Fraction(X[1])
def valExp(X):
    if (X[0]==0 and X[1]==0):
        print('error: zero raised to zero power')
        return
    return X[0]**X[1]
def valUnaryPlus(X): return X[0]
def valUnaryMinus(X): return -X[0]
def valFloor(X): return int(math.floor(X[0]))
def valCeil(X): return int(math.ceil(X[0]))
def valAbs(X):return abs(X[0])
def valMod(X):
    if X[1]==0:
        print('error: mod by zero')
        return
    else:
        m = Fraction(X[0]) % Fraction(X[1])
        if m==Fraction(0,1):
            return 0
        return m

def valLess(X): return X[0]< X[1]
def valGreater(X): return X[0] > X[1]
def valLesEq(X): return X[0]<=X[1]
def valGreatEq(X): return X[0]>=X[1]

# respective equality
def respEqual(X):
    (t1,a),(t2,b) = X
    return len(a)==len(b) and all([valEq([a[i],b[i]]) for i in range(len(a))])
# vector functions
def valCat(X): return ('seq', X[0][1]+X[1][1])
def valLen(X): return len(X[0][1])
def valSub(X):
    L = X[0][1]
    index = X[1]
    return L[index-1]

# set operations
def valIn(X):
    #if isSet(X[1]):
    return X[0] in X[1][1]
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))
def valSetEq(X): 
    if isSet(X[0]) and isSet(X[1]):
        return X[0][1]==X[1][1]
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))    
def valSubeq(X):
    if isSet(X[0]) and isSet(X[1]) :
        return X[0][1].issubset(X[1][1])
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))    
def valUnion(X): 
    if isSet(X[0]) and isSet(X[1]) :
        fs = frozenset(X[0][1])
        fs1 = frozenset(X[1][1])
        return ('set',fs.union(fs1))
        #return ('set',X[0][1].union(X[1][1]))
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))    
def valNrsec(X):
    if isSet(X[0]) and isSet(X[1]): return ('set',frozenset([e for e in X[0][1] if valIn([e,X[1]])]))
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))
def valSetSubtr(X):
    if isSet(X[0]) and isSet(X[1]): 
        return ('set',X[0][1].difference(X[1][1]))
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))
def valCrossProd(X):
    if isSet(X[0]) and isSet(X[1]): return ('set',frozenset([('tuple',(a,b)) for a in X[0][1] for b in X[1][1]]))
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))

#def valCardinal(X):
    #Arg = X[0]
    #elts = Arg[1]
    #return len([i for i in range(len(elts)) if not valIn([ elts[i], ('set',elts[i+1:]) ])])
def valPow(X):
    if not isSet(X[0]):
        print('Operation',Op,'not valid on arguments:',prettyArgs(Args))
        return
    [Arg] = X
    elts = Arg[1]
    # convert frozentset to list{
    elts = list(elts)
    if elts ==[] : return ('set',[('set',[])])
    head = elts[0]
    tail = elts[1:]
    S = valPow([('set',tail)])
    a=[]
    for e in S[1]:
        a = a + [('set',[head]+e[1])]
    return ('set',S[1] + a)
        
def valChoose(X):
    # The choice function of random is used for choosing a random element from the set.
    import random
    if isSet(X[0]): return random.choice(X[0][1])
    print('Operation',Op,'not valid on arguments:',prettyArgs(Args))    
def valIntRange(X):
    #s = []
    l,u = X
    if not (isIntegerValue(l) and isIntegerValue(u))  :
        print('Operation .. not valid on arguments:',prettyArgs(Args))            
        return
    #for i in range(int(l),int(u+1)):
        #s.append(i)
    s={i for i in range(int(l),int(u+1))}
    return ('set',frozenset(s))

def isIntegerValue(n):
    """
    helper functoin to check whether an LED object is an integer to prevent it to be a fraction whose dominator is 1
    """
    return isinstance(n,int) or isinstance(n,Fraction) and n.denominator==1
# Boolean connectives
def valAnd(X):
    p = val(X[0])
    if p==False: return False
    return val(X[1])
def valOr(X): return X[0] or X[1]
def valNot(X): return not(X[0])
def valImplies(Args):
    t= Args[1]
    p= Args[0]
    return all([val(dot(t,b)) for b in solutionSet(p)])

def valIff(X): return valImplies(X) and valImplies([X[1],X[0]])

# dynamic overloading resolution
def valPlus(X):
    if isNumber(X[0]) and isNumber(X[1]): return valAdd(X)
    if isVector(X[0]) and isVector(X[1]): return valCat(X)
    print('Operation + not valid on arguments:',prettyString(X[0]), 'and',prettyString(X[1]) )
def valPipes(X):
    if isNumber(X[0]): return valAbs(X)
    if isVector(X[0]) or isString(X[0]): return valLen(X)
    if isSet(X[0]): 
        return len(X[0][1])
        #return valCardinal(X)
    print('Operation || not valid on arguments:',prettyString(X[0]))    
def valEq(X):
    [a,b] = X
    if isSet(a) and isSet(b) : return valSetEq(X)
    if isVector(a) and isVector(b): return respEqual(X)
    if isTuple(a) and isTuple(b): return respEqual(X)
    if isNumber(a) and isNumber(b): return a==b
    if isSymbol(a) and isSymbol(b): return a==b
    if isString(a) and isString(b): return respEqual(X)
    return False
def valStar(X):
    if isNumber(X[0]) and isNumber(X[1]): return valMult(X)
    if isSet(X[0]) and isSet(X[1]): return valCrossProd(X)
    print('Operation * not valid on arguments:',prettyString(X[0]), 'and',prettyString(X[1]) )    

# quantifiers
def valSome(Args):
    # The AST of some var  in  t : s  is ('some',[var, A, B]), where A and B are the respective AST's of t and s. 
    # [var, A, B] = X
    var,t,s = Args
    if not isSet(val(t)):
        print('Operation some not valid on arguments:',prettyArgs([var,t]))
        return
    for i in val(t)[1]:
        if val(sub(i,var,s))==True:
            return True
    return False
def valAll(Args):
    # The AST of all var  in  t : s  is ('all',[var, A, B]), where A and B are the respective AST's of t and s. 
    # [var, A, B] = X
    var,t,s = Args
    if not isSet(val(t)):
        print('Operation some not valid on arguments:',prettyArgs([var,t]))
        return
    for i in val(t)[1]:
        if not val(sub(i,var,s))==True:
            return False
    return True

# lambda 
def valLambda(Args):
    return 1
# Big Operations

#The value of {t|p} is ('set',[val(dot(t,b)) for b in SolutionSet(p)]).
def valSetComp(Args):
    t= Args[0]
    p= Args[1]
    return ('set',frozenset([val(dot(t,b)) for b in solutionSet(p)]))

# The value of Union[p] T is ('set', [x for b in S(p) for x in val(dot(T,b))[1]]
def valBigUnion(Args):
    t= Args[1]
    p= Args[0]
    return ('set', tuple([x for b in solutionSet(p) for x in val(dot(t,b))[1]]))
#     slonSet = solutionSet(p)
#     #print(slonSet)
#     d = [[x for x in val(dot(t,b))[1]] for b in solutionSet(p)]
#     #print(Args)
#     #print(d)
#     return ('set',list(set(d[0]).union(*d)))
    
def valBigSum(Args):
    t= Args[1]
    p= Args[0]
    return sum([val(dot(t,b)) for b in solutionSet(p)])

from operator import mul
def valBigProd(Args):
    t= Args[1]
    p= Args[0]
    l = [val(dot(t,b)) for b in solutionSet(p)]
    if len(l)==0:
        return 1
    return reduce(mul, l)

def valBigNrsec(Args):
    t= Args[1]
    p= Args[0]
    slonSet = solutionSet(p)
    d = [[x for x in val(dot(t,b))[1]] for b in solutionSet(p)]
    return ('set',tuple(set(d[0]).intersection(*d)))


def valMember(Args):
    #print(Args)
    if Args[1]=='Nat':
        return isinstance(Args[0],int) and Args[0]>=0
    if Args[1]=='Bool':
        return isinstance(Args[0],bool)
    if Args[1]=='Int':
        return isinstance(Args[0],int) and not isinstance(Args[0],bool)
    if Args[1]=='Rat':
        return isRationalNum(Args)
    if Args[1]=='Seq':
        return isinstance(Args[0],tuple) and isinstance(Args[0][1],tuple) and Args[0][0]=='seq'
    if Args[1]=='fSet':
        return isTypeSet(Args)
    if Args[1]=='Lambda':
        return isTypeLambda(Args)
    if Args[1]=='Obj':
        return isObject(Args)
    if Args[1][0]=='set':
        return Args[0] in Args[1][1] 
    if isinstance(Args[1],tuple) and Args[1][0]=='star':
        return isTypeMember(Args[0],Args[1])
    if isinstance(Args[1],tuple) and Args[1][0]=='comStar':
        return isTypeMember(Args[0],Args[1][1][0])
    # fSet(type) or Seq(type)
    if Args[1][0]=='fSet' or Args[1][0]=='Seq':
        return all([valMember([x,Args[1][1][0]]) for x in Args[0][1]])
    # S U T where S and T are types
    if Args[1][0]=='U':
        return any([valMember([Args[0],t]) for t in Args[1][1]] )
    if isinstance(Args[1],str) and not Args[1] in BuiltInTypes:
        if Program.defined(Args[1],0):
            t =  Program.body(Args[1],0)
            valMember([Args[0],t])
    return False

def isTypeMember(Var,Type):
    '''tuple * tuple -> bool
    ''' #('tuple',[1,2]) : ('star',['Int','Int'])
    if isinstance(Var,tuple) and isinstance(Type,tuple) and Var[0]=='tuple':
        return all([valMember([Var[1][i],Type[1][i]]) for i in range(0,len(Var[1]))])
    # add param 

    if isinstance(Var,tuple) and Var[0]=='tuple' and not isinstance(Type,tuple) :
        #return all([valMember([Var[1][i],Type[1][i]]) for i in range(0,len(Var[1]))])
        return all([valMember([v,t]) for (v,t) in zip(Var[1],Type[1])])
    # 1:{1,2}
    #return valMember([Var,Type])
    return False
def isObject(Args):
    return isTypeSet(Args) or isTypeTuple(Args) or isRationalNum(Args) or isTypeLambda(Args)

def isTypeSet(Args):
    return isinstance(Args[0],tuple) and isinstance(Args[0][1],frozenset) and Args[0][0]=='set'

def isTypeTuple(Args):
    return isinstance(Args[0],tuple) and isinstance(Args[0][1],tuple) and Args[0][0]=='tuple'

def isRationalNum(Args):
    return isinstance(Args[0],int) or isinstance(Args[0],Fraction)

def isTypeLambda(Args):
    return isinstance(Args[0],tuple) and Args[0][0]=='lambda'

# builtIns is a dictionary of the functions that evaluate each built-in
builtIns = {'+':valPlus, '-':valSubtract, '*':valStar, '/':valDiv, '^':valExp,
            '+1':valUnaryPlus, '-1':valUnaryMinus,
            'floor':valFloor, 'ceil':valCeil, 'pipes':valPipes, 'mod':valMod,
            '=':valEq, '<':valLess, '>':valGreater,'<=':valLesEq,'>=':valGreatEq,
            'and':valAnd,'or' :valOr,'~':valNot,'=>':valImplies,'<=>':valIff,
            'sub':valSub,
            'in':valIn,'subeq':valSubeq,'U':valUnion,'nrsec':valNrsec,'\\':valSetSubtr,
            'Pow':valPow,'choose':valChoose,'intRange':valIntRange,'some':valSome,'all':valAll,'setComp':valSetComp,
            'Union':valBigUnion,'Sum':valBigSum,'Prod':valBigProd,'Nrsec':valBigNrsec,
            ':':valMember,
            'lambda':valLambda}

# Added by Qianji
"""
Solution sets

A *binding* is a set of pairs (x,v) where x is a variable and v is a term. If E is an expression and b a binding, we write E.b for the term obtained from E by substituting v for the free occurrences of x in E whenever (x,v) in b. 
For example,  x+y+z+p.{(x,1), (y,3), (z,4)} is the term 1+3+4+p. 
Binding b is a solution of sentence S if S.b is true. 
For example, {(x,1)} is a solution of x^2 = 1 but {(x,5)} is not.

Bindings b1 and b2 are *inconsistent* if there are pairs of the form (x,c1) and (x,c2) such that (x,c1) belongs to  b1, (x,c2) belongs to  b2, and the statement c1=c2 is false. 
Two bindings that are not inconsistent are said to be consistent.

The solution set of a sentence p, written S(p), is defined as follows, provided it can be computed by finitely applications of the following rules.

1.If p is a false ground sentence, then S(p)is the empty set { }. 
2.If p is a true ground sentence, then S(p) = { { } }. 
3.If p is of the form x = c, where x is a variable and c a ground term, then S(p) = {{(x,c)}}.
4.If p is of the form (x1,...,xn) = (c1,...,cn) where n>1, the xi's are distinct variables and the ci's are ground terms, then S(p) = {{(x1,c1),...,(xn,cn)}}.
5.If p is of the form x in c, where x is a variable and c is a ground term with value {c1,...,cn}, then S(p) = {{(x,c1)},...,{(x,cn}}. 
    Note that, by this definition, if c is the empty set the value of S(p) is { }. 
6.If p is of the form p1 p2,  then S(p) = S(p1) U S(p2).
7.If p is of the form p1 & p2, then S(p) = { b1 U b2 | b1 belongs to S(p1), b2 belongs to S(p2.b1), b1 consistent with b2 }.

The intuitive interpretation of the binding {(x1,c1),...,(xn,cn)} is x1=c1 &...&xn=cn. 
The intuitive interpretation of the solution set {b1,...,bn} is I(b1) or ... or I(bn), where I(b) is the interpretation of b. 
By this definition, the interpretation of the binding { } is true, the interpretation of the solution set { } is false, and the solution of the solution set { { } } is true.
"""
# AST -> bool
# isGround(E) iff t is a ground term
def isGround(E):
    if not isinstance(E,tuple) :
        if isScalar(E):
            return True
        if E in builtIns:
            return True
        if E in ['set','tuple','seq','string']:
            return True
        if Program.defined(E,0):
            return True
        else:
            return False
    (Op,Args) = E
    # special case for some/all var in term: sentence 
    if Op in ['some','all',':']:
        return True
    if isGround(Op) or Program.defined(Op,len(Args)):
        return all(isGround(i) for i in Args)
    return False

# AST -> set(bindings)
def solutionSet(E):
    """if E is an AST of a sentence p, then solutionSet(E) is the solution set of p """
    slonSet = []
    solution = []
    if isGround(E):
        #case 1
        #print(E,"is a ground term")
        #print(E)
        if val(E)==False:
            return []
        #case 2
        if val(E) == True:
            return [[]]
    else:
        Op,Args = E
        #case 3
        if Op =='=' and isinstance(Args[0],str) and isGround(Args[1]) :
            solution.append((Args[0],val(Args[1])))
            slonSet.append(solution)
            return slonSet
        # case 4
        if Op=='=' and isinstance(Args[0],tuple) and Args[0][0]=='tuple' and isGround(Args[1]) and val(Args[1])[0]=='tuple':
            C = val(Args[1])[1]
            X = Args[0][1]
            if len(X)==len(C):
                solution = []
                for i in range(len(X)):
                    solution.append((X[i],C[i]))
                slonSet.append(solution)
                return slonSet
        #case 5    
        if Op =='in' and isinstance(Args[0],str) and isGround(Args[1]) and val(Args[1])[0] =='set' :
            x = Args[0]
            C = val(Args[1])[1]
            for i in C:
                solution = []
                solution.append((x,i))
                slonSet.append(solution)
            return slonSet
            
        #case 6
        if Op =='or':
            p1 = Args[0]
            p2 = Args[1]
            Sp1 = solutionSet(p1)
            Sp2 = solutionSet(p2)
            return unionSlonSets(Sp1, Sp2)
        
        # case 7
        if Op =='and':
            p1 = Args[0]
            p2 = Args[1]
#             if p1 ==('all', ['c', 'gameBoard', ('~', [('moveMade', ['c'])])]):
#                 print(p1)
            #print(p1)
            Sp1 = solutionSet(p1)
            if Sp1 ==None:
                print(p1)
                return []
            slonSet = []
            for i in range(len(Sp1)):
                b1 = Sp1[i]
                Sp2_b1 = solutionSet(subExpression(p2,b1))
                if Sp2_b1 ==None: 
                    print (subExpression(p2,b1))
                    return []
                for j in range(len(Sp2_b1)):
                    b2 = Sp2_b1[j]
                    if areConsistent(b1, b2):
                        union = unionBindings(b1,b2)
                        slonSet.append(union)
            return slonSet
                        
                    
"""
 If E is an expression and b a binding, we write E.b for the term obtained from E by substituting v for the free occurrences of x in E whenever (x,v) in b. 
 For example,  x+y+z+p.{(x,1), (y,3), (z,4)} is the term 1+3+4+p. 
"""            
# AST * list(tuple) -> AST
def subExpression(E,b): 
    if b==None: return E
    params = [ i[0] for i in b]
    vals = [val(i[1]) for i in b]
    sub =subAll(vals,params,E)
    #if val(sub)==True:
    #    return sub
    #return ('=',[1,0])
    return sub
#solution set * solution set -> solution set
def unionSlonSets(Sp1,Sp2):
    slonSet =[]
    slonSet = Sp1.copy()
    for i in range(len(Sp2)):
        if not Sp2[i] in slonSet:
            slonSet.append(Sp2[i])
    return slonSet

# binding * binding -> binding
def unionBindings(b1,b2):
    b=[]
    b = b1.copy()
    for i in range(len(b2)):
        if not b2[i] in b:
            b.append(b2[i])
    return b
#list(tuple) * list(tuple) -> bool
# If b1 and b2 are bindings, areConsistent(b1,b2) iff b1 is consistent with b2
def areConsistent(b1,b2):                
    for i in range(len(b1)):
        for j in range(len(b2)):
            if(b1[0]==b2[0]):
                if not val(b1[1]) == val(b2[1]):
                    return False
    return True

#dot(t,b) is a Python expression whose value represents t.b. 
def dot(t,b):
    e = subExpression(t,b)
    return val(e)
     # find the solution set of the guard condition


