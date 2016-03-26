'''
Qianji
March 2015
This file is created to be called in the server to evaluate an expression
'''

import sys
from LED.Tokenizer import *
from LED.Expression import *
from LED.LEDProgram import *
from LED.Evaluater import val
from LED.Parser import *
from LED.Compiler import *

def evaluateLEDExpression(command):
    e = command
    try:
        expression,eFlag = tokens(e)
    except:
        return 'Failed to tokenize the expression.The last 10 valid tokens are' + ' ' +' '.join(expression[-10:])
    if eFlag:
        try:
            tree, tFlag = parseExpression(expression)
        except:
            return 'Failed to parse the expression or definition.'
        if tFlag:
            try:
                value = val(tree.expression())
                if not value ==None:
                    if isinstance(value,Fraction):
                        value = numeralValue(value)
                    return prettyString(value)
            except:
                return 'Failed to evaluate the expression. It is not a valid expression'
            return 'Failed to evaluate the expression. It is not a valid expression'
        d,defFlag = parseDfn(expression)
        if defFlag:
            #print('parsing #',i,"function successfully",' '.join(funcs[i]))
            Program.update(d)
        else:
            return 'Failed to parse the expression or definition.'
    else:
        return 'Failed to tokenize the expression.The last 10 valid tokens are' + ' ' +  ' '.join(expression[-10:])

#evaluateLEDExpression()

