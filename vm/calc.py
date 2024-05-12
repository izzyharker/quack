from lark import Lark, Transformer, v_args
import logging
import os
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# try:
#     input = raw_input   # For Python2 compatibility
# except NameError:
#     pass

# IMPORTANT: class name has to match file name for tiny_vm to run
ASM_FILE = "Calculator.asm"

calc_grammar = """
    ?start: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""

@v_args(inline=True)
class EmitCode(Transformer):
    """
    Copying from 
    """
    def __init__(self):
        log.debug("EmitCode constructor")

        # set output file for writing
        self.out_file = ASM_FILE

    def add(self, left, right):
        log.debug('sum "+" product -> add')
        with open(self.out_file, "a") as f:
            print("\tcall Int:plus", file=f)
        f.close()

    def product(self):
        log.debug("?product")
    
    def sum(self):
        log.debug("?sum")

    def sub(self, left, right):
        log.debug('sum "-" product -> sub')
        with open(self.out_file, "a") as f:
            print("\tcall Int:minus", file=f)
        f.close()

    def mul(self, left, right):
        log.debug('product "*" atom -> mul')
        with open(self.out_file, "a") as f:
            print("\tcall Int:multiply", file=f)
        f.close()

    def div(self, left, right):
        log.debug('product "/" atom -> div')
        with open(self.out_file, "a") as f:
            print("\tcall Int:divide", file=f)
        f.close()

    def number(self, v):
        log.debug(f'number: {v}')
        with open(self.out_file, "a") as f:
            print(f"\tconst {v}", file=f)
        f.close()

    def neg(self, v):
        log.debug('"-"atom -> neg')
        with open(self.out_file, "a") as f:
            print("\tcall Int:negate", file=f)
        f.close()

calc_parser = Lark(calc_grammar, parser='lalr', transformer=EmitCode())
calc = calc_parser.parse

def main():
    # delete the file if it exists
    # i think the "w" flag would also solve this problem but i am lazy
    # maybe i will change this maybe not
    # nobody knows
    try:
        open(ASM_FILE, "x")
    except FileExistsError:
        os.remove(ASM_FILE)

    # write header information
    f = open(ASM_FILE, "a")
    print(".class Calculator:Obj", file=f)
    print(".method $constructor", file=f)
    print("\tenter", file=f)

    f.close()

    # logging
    print("Starting code generation...")
    print("Enter any number of arithmetic expressions, then 'q' to evaluate.")

    # loop to collect expressions
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        if s == "q":
            break
        
        # parse the expression
        # if it's invalid, break the loop
        try:
            calc(s)
        except:
            log.info("Error: invalid expression. Exiting input (previous expressions will be evaluated)...")
            break

        # after each expression, print the result and a newline
        f = open(ASM_FILE, "a")
        print("\tcall Int:print", file=f)
        print('\tconst "\\n"', file=f)
        print("\tcall String:print", file=f)
        f.close()

    # write the return statement
    f = open(ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()
        

if __name__ == '__main__':
    main()