import os
import readline
import glob
import re  # Add this import to fix the 're' module error

class Completer(object):
    RE_SPACE = re.compile(r'.*\s+$', re.M)  # Use a raw string to fix the warning

    def _listdir(self, root):
        """List the files and directories in the given root directory."""
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
                res.append(name[:-1])
            else:
                if name.endswith('.py'):  # Only return Python files
                    res.append(name[:-3])  # Remove ".py" extension
        return res

    def _complete_path(self, path):
        """Complete file or directory path."""
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in self._listdir(tmp) if p.startswith(rest)]
        if len(res) > 1 or not os.path.exists(path):
            return res

        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]

        return [path + ' ']

    def complete_use(self, args):
        """Complete the 'use' command (module names)."""
        if not args:
            return self._complete_path(modulesPath)

        result = self._complete_path(modulesPath + args[-1])
        for i in range(len(result)):
            result[i] = result[i].replace(modulesPath, '')
        return result

    def complete_show(self, args):
        """Complete the 'show' command (options or modules)."""
        if args[0] == '':
            return ['modules', 'options']
        if 'modules'.startswith(args[0]):
            return ['modules']
        elif 'options'.startswith(args[0]):
            return ['options']

    def complete_set(self, args):
        """Complete the 'set' command (options of the selected module)."""
        if POINTER:
            result = []
            for option in modules[POINTER].options:
                if option.startswith(args[0]):
                    result.append(option)
            return result

    def complete(self, text, state):
        """Main completion function for all commands."""
        buffer = readline.get_line_buffer()
        line = buffer.split()

        if self.RE_SPACE.match(buffer):
            line.append('')

        cmd = line[0].strip()
        if cmd in Command.COMMANDS:
            impl = getattr(self, f'complete_{cmd}', None)
            if impl:
                args = line[1:]
                if args:
                    return (impl(args) + [None])[state]
                return [cmd + ' '][state]
        
        # Return the completions for commands that start with the input
        results = [c + ' ' for c in Command.COMMANDS if c.startswith(cmd)] + [None]
        return results[state]
