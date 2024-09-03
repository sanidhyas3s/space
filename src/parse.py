def get_param(code, index):
    if(index >= len(code) or code[index] not in (" ", "\t")):
        raise ValueError("Expected number, got EOF")
    sign = 1 if code[index] == " " else -1
    number = ""
    index += 1
    number = ""
    while(index < len(code) and code[index] != '\n'):
        number += '1' if code[index] == '\t' else '0'
        index += 1
    if index >= len(code):
        raise ValueError("Expected newline, got EOF")
    if number == "":
        return 0, index+1
    return sign * int(number,2), index+1

def check_length(index, code):
    if index >= len(code):
        raise ValueError("Early EOF")
    return index

def preprocess(code):
    return "".join([c for c in code if c in (" ", "\t", "\n")])

def remove_dead(instructions):
    """
    This prevents errors when dead code between unconditional jumps is present,
    which is caused due to LLVM IR "Block" semantics.
    """
    search = False
    instructions_new = []
    for (actions, param) in instructions:
        if(search and actions == "FLOW_MARK"):
            search = False
        if(not search):
            instructions_new.append((actions, param))
        if(actions == "FLOW_JUMP"):
            search = True
    return instructions_new

def get_next_instruction(code, index):
    index = check_length(index, code)
    if(code[index] == ' '):
        index = check_length(index+1, code)        
        if(code[index] == ' '):
            param, index = get_param(code, index+1)
            return "STACK_PUSH", param, index
        check_length(index+1, code)
        if(code[index:index+2] == "\n "):
            return "STACK_DUP", None, index+2
        elif(code[index:index+2] == "\t "):
            param, index = get_param(code, index+2)
            return "STACK_COPY", param, index
        elif(code[index:index+2] == "\n\t"):
            return "STACK_SWAP", None, index+2
        elif(code[index:index+2] == "\n\n"):
            return "STACK_DISCARD", None, index+2
        elif(code[index:index+2] == "\t\n"):
            param, index = get_param(code, index+2)
            return "STACK_SLIDE", param, index+2
    elif(code[index] == '\n'):
        check_length(index+2, code)
        index += 1
        if(code[index:index+2] == "  "):
            param, index = get_param(code, index+2)
            return "FLOW_MARK", param, index
        elif(code[index:index+2] == " \n"):
            param, index = get_param(code, index+2)
            return "FLOW_JUMP", param, index
        elif(code[index:index+2] == "\t "):
            param, index = get_param(code, index+2)
            return "FLOW_JZERO", param, index
        elif(code[index:index+2] == "\t\t"):
            param, index = get_param(code, index+2)
            return "FLOW_JNEG", param, index
            """
            SUBROUTINES (CALL & RET)
            NOT IMPLEMENTED IN LLVM, DUE TO
            INSUFFICIENT DOCUMENTATION
            """
        elif(code[index:index+2] == " \t"):
            param, index = get_param(code, index+2)
            return "FLOW_CALL", param, index
        elif(code[index:index+2] == "\t\n"):
            return "FLOW_RET", None, index+2
        elif(code[index:index+2] == "\n\n"):
            return "FLOW_EXIT", None, index+2
    elif(code[index] == '\t'):
        index = check_length(index+1, code)
        if(code[index] == '\n'):
            index += 1
            check_length(index+1, code)
            if(code[index:index+2] == "  "):
                return "IO_PUTCHAR", None, index+2
            elif(code[index:index+2] == " \t"):
                return "IO_PUTNUM", None, index+2
            elif(code[index:index+2] == "\t "):
                return "IO_GETCHAR", None, index+2
            elif(code[index:index+2] == "\t\t"):
                return "IO_GETNUM", None, index+2
        elif(code[index] == ' '):
            index += 1
            check_length(index+1, code)
            if(code[index:index+2] == "  "):
                return "MATH_ADD", None, index+2
            elif(code[index:index+2] == " \t"):
                return "MATH_SUB", None, index+2
            elif(code[index:index+2] == " \n"):
                return "MATH_MUL", None, index+2
            elif(code[index:index+2] == "\t "):
                return "MATH_DIV", None, index+2
            elif(code[index:index+2] == "\t\t"):
                return "MATH_MOD", None, index+2
        elif(code[index] == '\t'):
            index = check_length(index+1, code)
            if(code[index] == ' '):
                return "HEAP_STORE", None, index+1
            elif(code[index] == '\t'):
                return "HEAP_LOAD", None, index+1

# test code
if __name__ == "__main__":
    code = "   \t  \t   \n\t\n      \t\t \t  \t\n\t\n  \n\n\n"
    code = preprocess(code)
    instructions = []
    index = 0
    print("INSTRUCTION, PARAMETER, NEXT INDEX:")
    while(index<len(code)):
        instruction, param, index = get_next_instruction(code, index)
        print(instruction, param, index)
        instructions.append((instruction, param))