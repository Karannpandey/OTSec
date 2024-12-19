import os
import importlib.util

class Plugins:
    pluginTree = list()
    modules = dict()

    def __init__(self, path):
        self.path = os.path.abspath(path)  # Ensure absolute path

    def crawler(self):
        print(f"Scanning directory: {self.path}")
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith('.py'):
                    relative_path = os.path.relpath(os.path.join(root, file), self.path)
                    module_path = relative_path.replace('.py', '').replace(os.sep, '/')
                    print(f"Discovered module: {module_path}")
                    self.pluginTree.append(module_path.split('/'))

    def load(self):
        for plugin in self.pluginTree:
            name = plugin[-1]
            item = '/'.join(plugin)
            file_path = os.path.join(self.path, *plugin) + '.py'

            print(f"Loading module: {item} from {file_path}")
            if not os.path.exists(file_path):
                print(f"Error: File does not exist at {file_path}")
                continue

            try:
                spec = importlib.util.spec_from_file_location(name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'Module'):
                    self.modules[item] = module.Module()
                    print(f"Successfully loaded module: {item}")
                else:
                    print(f"Error: 'Module' class not found in {file_path}")

            except Exception as e:
                print(f"Error while loading module {item}: {e}")

