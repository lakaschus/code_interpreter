import time
import multiprocessing
import ast
import sys
import traceback
import contextlib
import io
import logging
import astunparse

class CodeInterpreter:

    def __init__(self, task_id, code_text):
        self.code_text = code_text
        self.task_id = task_id
        self.start_time = time.time()
        self.logger = logging.getLogger('CodeInterpreter')
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(f'out/{task_id}.log')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def is_code_safe(self, tree):
        return True

    def format_code(self):
        # Parse the code into an AST
        tree = ast.parse(self.code_text)

        # Convert the AST back into a string of code
        formatted_code = astunparse.unparse(tree)

        return formatted_code

    def execute_code(self):
        try:
            # formatted_code = self.format_code()
            tree = ast.parse(self.code_text, mode='exec')
        except SyntaxError as e:
            self.logger.error('Invalid syntax')
            return

        if not self.is_code_safe(tree):
            self.logger.error('Forbidden code structure')
            return

        exec_globals = {}
        exec_locals = {}

        # Redirect stdout and stderr to log file
        f = io.StringIO()
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            try:
                exec(self.code_text, exec_globals, exec_locals)
                self.logger.info('Execution Result: %s', exec_locals)
            except Exception:
                _, _, tb = sys.exc_info()
                self.logger.error('Error during execution: \n%s', traceback.format_exception(*sys.exc_info()))

        self.logger.info('Execution output: %s', f.getvalue())


def main(example):
    code_interpreter = CodeInterpreter("test", example)
    code_interpreter.execute_code()
    print("Time taken: ", time.time() - code_interpreter.start_time)


if __name__ == "__main__":
    # Get example from tests/code.txt
    example = open("tests/code.txt", "r").read()
    main(example)
