import llvmlite.ir as ir
import llvmlite.binding as llvm
import os, sys, tempfile, subprocess
import parse

"""
Global Declarations
"""
STACK_SIZE = 64
HEAP_SIZE = 64

int_32 = ir.IntType(32)
int_8 = ir.IntType(8)


def get_str(builder, string):
    fmt = bytearray((string + "\0").encode("utf-8"))
    c_str = ir.Constant(ir.ArrayType(int_8, len(fmt)), fmt)
    ptr = builder.alloca(c_str.type)
    builder.store(c_str, ptr)
    return ptr

def increment(builder, ptr):
    builder.store(builder.add(builder.load(ptr), ir.Constant(int_32, 1)), ptr)

def decrement(builder, ptr):
    builder.store(builder.sub(builder.load(ptr), ir.Constant(int_32, 1)), ptr)

def compiler(builder, code):
    printf_func = ir.Function(builder.module, ir.FunctionType(int_32, [], var_arg = True), "printf")
    scanf_num = ir.Function(builder.module, ir.FunctionType(int_32, [], var_arg = True), "scanf")

    stack = ir.Constant(ir.ArrayType(int_32, STACK_SIZE), [0] * STACK_SIZE)
    stack_ptr = builder.alloca(stack.type)
    builder.store(stack, stack_ptr)
    
    heap = ir.Constant(ir.ArrayType(int_32, STACK_SIZE), [0] * STACK_SIZE)
    heap_ptr = builder.alloca(heap.type)
    builder.store(heap, heap_ptr)

    # heap = ir.Constant(ir.ArrayType(int_32, HEAP_SIZE), [0] * HEAP_SIZE)
    # heap_ptr = builder.alloca(heap.type)
    # builder.store(heap, heap_ptr)

    top = ir.Constant(int_32, -1)
    top_ptr = builder.alloca(top.type)
    builder.store(top, top_ptr)
    
    code = parse.preprocess(code)
    instructions = []
    index = 0
    while(index<len(code)):
        instruction, param, index = parse.get_next_instruction(code, index)
        instructions.append((instruction, param))
        print(instruction, param)
    print("\n")
    instructions = parse.remove_dead(instructions)

    blocks = {}
    subroutines = []
    possible = None
    for (action, param) in instructions:
        if action == "FLOW_MARK" and not blocks.get(param):
            if possible is not None:
                blocks[possible] = builder.append_basic_block("label"+str(possible))
            possible = param
        elif action == "FLOW_MARK":
            raise Exception("Label already defined: " + str(param))
        elif action == "FLOW_RET":
            if(possible is None):
                raise Exception("Flow return without subroutine definition")
            subroutines.insert(possible)
            possible = None
    if possible is not None:
        blocks[possible] = builder.append_basic_block("label"+str(possible))
    """
    SUBROUTINES ARE NOT IMPLEMENTED (BECAUSE OF INSUFFICIENT DOCUMENTATION)
    AND WOULD NOT COMPILE PROPERLY
    """
    
    block_terminated = False
    for (action, param) in instructions:
        if(action == "STACK_PUSH"):
            increment(builder, top_ptr)
            tmp_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            builder.store(ir.Constant(int_32, param), tmp_ptr)
        elif(action == "STACK_DUP"):
            tmp = builder.load(builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))
            increment(builder, top_ptr)
            tmp_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            builder.store(tmp, tmp_ptr)
        elif(action == "STACK_COPY"):
            if(param > 0):
                increment(builder, top_ptr)
                nth_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, param))
                nth_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), nth_index])
                builder.store(builder.load(nth_ptr), builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))
            elif(param < 0):
                nth_index = builder.sub(ir.Constant(int_32, -1), ir.Constant(int_32, param))
                increment(builder, top_ptr)
                nth_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), nth_index])
                builder.store(builder.load(nth_ptr), builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))
        elif(action == "STACK_SWAP"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(tmp1, tmp2_ptr)
            builder.store(tmp2, tmp1_ptr)
        elif(action == "STACK_DISCARD"):
            decrement(builder, top_ptr)
        elif(action == "STACK_SLIDE"):
            tmp_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp = builder.load(tmp_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, param)), top_ptr)
            builder.store(tmp, builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))
        elif(action == "MATH_ADD"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(builder.add(tmp1, tmp2), tmp2_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1)), top_ptr)
        elif(action == "MATH_SUB"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(builder.sub(tmp1, tmp2), tmp2_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1)), top_ptr)
        elif(action == "MATH_MUL"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(builder.mul(tmp1, tmp2), tmp2_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1)), top_ptr)
        elif(action == "MATH_DIV"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(builder.sdiv(tmp1, tmp2), tmp2_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1)), top_ptr)
        elif(action == "MATH_MOD"):
            tmp1_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            tmp1 = builder.load(tmp1_ptr)
            second_index = builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1))
            tmp2_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), second_index])
            tmp2 = builder.load(tmp2_ptr)
            builder.store(builder.srem(tmp1, tmp2), tmp2_ptr)
            builder.store(builder.sub(builder.load(top_ptr), ir.Constant(int_32, 1)), top_ptr)
        elif(action == "IO_PUTCHAR"):
            builder.call(printf_func, args = [get_str(builder, "%c"), builder.load(builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))])
            decrement(builder, top_ptr)
        elif(action == "IO_PUTNUM"):
            builder.call(printf_func, args = [get_str(builder, "%d"), builder.load(builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)]))])
            decrement(builder, top_ptr)
        elif(action == "IO_GETCHAR"):
            int_ptr = builder.alloca(int_32)
            builder.call(scanf_num, args=[get_str(builder, "%c"), int_ptr])
            value = builder.load(int_ptr)
            increment(builder, top_ptr)
            tmp_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            builder.store(value, tmp_ptr)
        elif(action == "IO_GETNUM"):
            int_ptr = builder.alloca(int_32)
            builder.call(scanf_num, args=[get_str(builder, "%d"), int_ptr])
            value = builder.load(int_ptr)
            increment(builder, top_ptr)
            tmp_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            builder.store(value, tmp_ptr)
        elif(action == "HEAP_STORE"):
            value_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            value = builder.load(value_ptr)
            decrement(builder, top_ptr)
            addr_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            decrement(builder, top_ptr)
            builder.store(value, builder.gep(heap_ptr, [ir.Constant(int_32, 0), builder.load(addr_ptr)]))
        elif(action == "HEAP_LOAD"):
            addr_ptr = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            addr = builder.load(addr_ptr)
            heap_addr = builder.gep(heap_ptr, [ir.Constant(int_32, 0), addr])
            value = builder.load(heap_addr)
            stack_top = builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])
            builder.store(value, stack_top)
        elif(action == "FLOW_MARK"):
            if not block_terminated:
                builder.branch(blocks[param])
            block_terminated = False
            builder.position_at_end(blocks[param])
        elif(action == "FLOW_JUMP"):
            if (param not in blocks):
                raise Exception("Undeclared label: " + str(param))
            block_terminated = True
            builder.branch(blocks[param])
        elif(action == "FLOW_JZERO"):
            if (param not in blocks):
                raise Exception("Undeclared label: " + str(param))
            res = builder.icmp_signed("==", builder.load(builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])), ir.Constant(int_32, 0))
            decrement(builder, top_ptr)
            next = builder.append_basic_block()
            builder.cbranch(res, blocks[param], next)
            builder.position_at_end(next)
        elif(action == "FLOW_JNEG"):
            res = builder.icmp_signed("<", builder.load(builder.gep(stack_ptr, [ir.Constant(int_32, 0), builder.load(top_ptr)])), ir.Constant(int_32, 0))
            decrement(builder, top_ptr)
            next = builder.append_basic_block()
            builder.cbranch(res, blocks[param], next)
            builder.position_at_end(next)
        elif(action == "FLOW_CALL"):
            pass
        elif(action == "FLOW_RET"):
            pass
        elif(action == "FLOW_EXIT"):
            builder.ret(ir.Constant(int_32, 0))
            block_terminated = True

def clean():
    src_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_path)
    temp = ["temp.llvm", "temp_opt.llvm", "temp.bc", "temp.o"]
    for file in temp:
        file = "../temp/" + file
        if(os.path.exists(file)):
            os.remove(file)

    print("\U0001F5D1", end = " ")
    print("Temporary files removed.")
    return

def main(argv):
    if(argv[1] == "CLEAN"):
        clean()
        return 0

    module = ir.Module()
    main_func = ir.Function(module, ir.FunctionType(int_32, []), "main")
    builder = ir.IRBuilder(main_func.append_basic_block("entry"))

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    module.triple = target_machine.triple

    code = open(argv[1], "r").read()
    compiler(builder, code)

    filename = os.path.split(os.path.splitext(argv[1])[0])[1]
    executable = "../exe/" + filename + (".exe" if sys.platform == "win32" else "")

    src_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tempfile.gettempdir())
    os.chdir(src_path)

    with open("../temp/temp.llvm", "w") as file:
        file.write(str(module))
    print(module)

    subprocess.run(["opt", "../temp/temp.llvm", "-o", "../temp/temp.bc"], capture_output = True)
    subprocess.run(["llvm-dis", "../temp/temp.bc", "-o", "../temp/temp_opt.llvm"])
    subprocess.run(["llc", "-filetype=obj", "../temp/temp_opt.llvm", "-o", "../temp/temp.o"])
    subprocess.run(["g++", "../temp/temp.o", "-o", executable])

    with open(executable, "rb") as file:
        data = file.read()

    os.remove(executable)

    with open(executable, "wb") as file:
        file.write(data)
        
    if(sys.platform != "win32"):
        subprocess.run(["chmod","+x",executable])

if __name__ == "__main__":
    sys.exit(main(sys.argv))