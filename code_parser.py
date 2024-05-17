import ast


class Code:
    def __init__(self, path):
        self.path = path
        self.functions = []
        self.classes = []
        self.get_params()

    class CodeBlock:
        def __init__(self, name, start_line, end_line):
            self.name = name
            self.start_line = start_line
            self.end_line = end_line

    class Function(CodeBlock):
        def __init__(self, name, start_line, end_line, body):
            super().__init__(name, start_line, end_line)
            self.functions = []
            self.classes = []
            self.get_inner_objects(body)

        def get_inner_objects(self, body):
            for obj in body:
                if isinstance(obj, ast.FunctionDef):
                    self.functions.append(Code.Function(obj.name, obj.lineno, obj.end_lineno, obj.body))
                if isinstance(obj, ast.ClassDef):
                    self.classes.append(Code.Class(obj.name, obj.lineno, obj.end_lineno, obj.body))

        def __str__(self):
            functions_str = '\n'.join(str(f) for f in self.functions)
            inner_classes_str = '\n'.join(str(c) for c in self.classes)
            return f'Function name: {self.name}\n\tStart: {self.start_line}\n\tEnd: {self.end_line}\n' \
                   f'Inner functions:\n{functions_str if functions_str else "-"}\n' \
                   f'Inner classes:\n{inner_classes_str if inner_classes_str else "-"}\n'

    class Class(CodeBlock):
        def __init__(self, name, start_line, end_line, body):
            super().__init__(name, start_line, end_line)
            self.functions = []
            self.classes = []
            self.get_inner_objects(body)

        def get_inner_objects(self, body):
            for obj in body:
                if isinstance(obj, ast.FunctionDef):
                    self.functions.append(Code.Function(obj.name, obj.lineno, obj.end_lineno, obj.body))
                if isinstance(obj, ast.ClassDef):
                    self.classes.append(Code.Class(obj.name, obj.lineno, obj.end_lineno, obj.body))

        def __str__(self):
            methods_str = '\n'.join(str(method) for method in self.functions)
            inner_classes_str = '\n'.join(str(c) for c in self.classes)
            return f'Class name: {self.name}\n\tStart: {self.start_line}\n\t' \
                   f'End: {self.end_line}\nMethods:\n{methods_str if methods_str else "-"}\n' \
                   f'Inner classes:\n{inner_classes_str if inner_classes_str else "-"}\n'

    def get_params(self):
        with open(self.path) as file:
            node = ast.parse(file.read())
        for obj in node.body:
            if isinstance(obj, ast.FunctionDef):
                self.functions.append(Code.Function(obj.name, obj.lineno, obj.end_lineno, obj.body))
            elif isinstance(obj, ast.ClassDef):
                self.classes.append(Code.Class(obj.name, obj.lineno, obj.end_lineno, obj.body))

    def __str__(self):
        classes_str = '\n'.join(str(cur_class) for cur_class in self.classes)
        functions_str = '\n'.join(str(cur_function) for cur_function in self.functions)
        return f'CODE CLASSES:\n-------------------------------\n{classes_str}-------------------------------\n' \
               f'CODE FUNCTIONS:\n-------------------------------\n{functions_str}\n-------------------------------\n'

    def get_code(self, block):
        start, end = block.start_line, block.end_line
        with open(self.path) as file:
            code_text = file.read().split('\n')
        return '\n'.join(code_text[start - 1:end])
