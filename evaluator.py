def choose_best_version(

    original_code,
    original_benchmark,

    optimized_code,
    optimized_benchmark
):

    # If optimized version failed
    if not optimized_benchmark["success"]:

        return {
            "winner": "original",
            "code": original_code
        }

    # Compare runtime
    if optimized_benchmark["runtime"] < original_benchmark["runtime"]:

        return {
            "winner": "optimized",
            "code": optimized_code
        }

    return {
        "winner": "original",
        "code": original_code
    }