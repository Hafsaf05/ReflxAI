import timeit
import tracemalloc


def benchmark_code(code):

    tracemalloc.start()

    try:

        runtime = timeit.timeit(
            stmt=code,
            number=1
        )

        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        return {
            "runtime": runtime,
            "memory": peak,
            "success": True
        }

    except Exception as e:

        tracemalloc.stop()

        return {
            "success": False,
            "error": str(e)
        }