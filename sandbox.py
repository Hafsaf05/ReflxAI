import subprocess
import tempfile

def run_code(code):

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as temp_file:

        temp_file.write(code)

        filename = temp_file.name

    try:

        result = subprocess.run(
            ["python", filename],

            input="10\n2\n",

            capture_output=True,
            text=True,

            timeout=5
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:

        return {
            "stdout": "",
            "stderr": "Execution timed out."
        }