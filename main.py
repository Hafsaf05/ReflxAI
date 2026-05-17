from generator import generate_code, fix_code
from sandbox import run_code
from critique import critique_code, optimize_code
from memory import store_memory, retrieve_memory
from benchmark import benchmark_code
from evaluator import choose_best_version

task = input("Enter coding task: ")

print("\nGenerating code...\n")

memories = retrieve_memory(task)

print("\nMEMORY RETRIEVAL:\n")
print(memories)

code = generate_code(task, memories)

max_attempts = 3

for attempt in range(max_attempts):

    print(f"\nATTEMPT {attempt + 1}")
    print("\nCODE:\n")
    print(code)

    print("\nRunning code...\n")

    result = run_code(code)

    if result["stderr"] == "":

        print("SUCCESS!\n")

        print("OUTPUT:\n")
        print(result["stdout"])

        print("\nBENCHMARK:\n")

        benchmark = benchmark_code(code)

        print(benchmark)

        print("\nCRITIQUE:\n")

        critique = critique_code(code)

        print(critique)

        print("\nOPTIMIZING CODE...\n")

        optimized_code = optimize_code(code, critique)

        print("OPTIMIZED CODE:\n")

        print(optimized_code)

        print("\nOPTIMIZED BENCHMARK:\n")

        optimized_benchmark = benchmark_code(optimized_code)

        print(optimized_benchmark)

        decision = choose_best_version(code, benchmark, optimized_code, optimized_benchmark)

        print("\nBEST VERSION:\n")

        print(decision["winner"])
        print("\nFINAL CODE:\n")
        print(decision["code"])

        break

    else:

        print("FAILED!\n")
        store_memory(task, result["stderr"])

        print("ERROR:\n")
        print(result["stderr"])

        print("\nFixing code...\n")

        code = fix_code(
            code,
            result["stderr"]
        )

else:

    print("\nMax attempts reached.")