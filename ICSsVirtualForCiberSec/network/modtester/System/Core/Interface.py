import sys
import os
from .Global import *
import readline
from System.Core.Loader import Plugins  # Import 'Plugins' from Loader.py
from .Colors import bcolors
from .Banner import Banner
from Lib import prettytable
from System.Core.Completer import Completer

modulesPath = 'Application/modules/'  # Update this to the correct path

# Global variables
POINTER = None  # Initialize POINTER

# Command class for handling different commands
class Command:
    COMMANDS = ['back', 'exit', 'exploit', 'help', 'show', 'set', 'use']
    helpCommand = [
        ['back', 'Move back from the current context'],
        ['exit', 'Exit the console'],
        ['exploit', 'Run module'],
        ['help', 'Help menu'],
        ['show', 'Displays modules of a given type, or all modules'],
        ['set', 'Sets a variable to a value'],
        ['use', 'Selects a module by name']
    ]

    def __init__(self):
        self.variables = {}  # Store variables set by the 'set' command

    def help(self, args, pointer=None):
        table = prettytable.PrettyTable([bcolors.BOLD + 'Command' + bcolors.ENDC, bcolors.BOLD + 'Description' + bcolors.ENDC])
        table.border = False
        table.align = 'l'
        table.add_row(['-'*7, '-'*11])
        for i in self.helpCommand:
            table.add_row([bcolors.OKBLUE + i[0] + bcolors.ENDC, i[1]])
        print(table)

    def exit(self, args, pointer=None):
        sys.exit(0)

    def back(self, args, pointer=None):
        global POINTER
        POINTER = None

    def show(self, args, pointer=None):
        if len(args) < 2:
            return None
        if args[1] == 'modules':
            table = prettytable.PrettyTable([bcolors.BOLD + 'Modules' + bcolors.ENDC, bcolors.BOLD + 'Description' + bcolors.ENDC])
            table.border = False
            table.align = 'l'
            table.add_row(['-'*7, '-'*11])
            for i in sorted(modules):
                table.add_row([bcolors.OKBLUE + i + bcolors.ENDC, modules[i].info['Description']])
            print(table)
        if args[1] == 'options':
            if pointer:
                table = prettytable.PrettyTable([bcolors.BOLD + 'Name' + bcolors.ENDC, bcolors.BOLD + 'Current Setting' + bcolors.ENDC, bcolors.BOLD + 'Required' + bcolors.ENDC, bcolors.BOLD + 'Description' + bcolors.ENDC])
                table.border = False
                table.align = 'l'
                table.add_row(['-'*4, '-'*15, '-'*8, '-'*11])
                for i in sorted(modules[pointer].options):
                    table.add_row([bcolors.OKBLUE + i + bcolors.ENDC, modules[pointer].options[i][0], modules[pointer].options[i][1], modules[pointer].options[i][2]])
                print(table)

    def use(self, args, pointer=None):
        global POINTER
        if len(args) < 2:
            return None
        POINTER = args[1]
        moduleName = args[1].split('/')
        comp = Completer()
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(comp.complete)
        while True:
            command_input = input('SMOD ' + moduleName[0] + '(' + bcolors.OKBLUE + moduleName[-1] + bcolors.ENDC + ') > ').strip().split()  # Renamed 'input' to 'command_input'
            try:
                result = getattr(self, command_input[0])(command_input, args[1])  # Replaced 'input' with 'command_input'
            except Exception as e:
                print(f"Error: {e}")
                return None
            if POINTER is None:
                break

    def set(self, args, pointer=None):
        if len(args) < 3:
            print("Error: Invalid syntax. Correct usage: set <variable> <value>")
            return
        variable_name = args[1]
        value = args[2]
        self.variables[variable_name] = value
        print(f"Set {variable_name} to {value}")
        if pointer and pointer in modules:
            print(f"Module options: {modules[pointer].options}")

    def exploit(self, args, pointer=None):
        if pointer:
            # Ensure the module exists
            if pointer not in modules:
                print(f"{bcolors.FAIL}[-]{bcolors.ENDC} Module '{pointer}' not found.")
                return

            # Check if all required options are set
            flag = True
            for option in modules[pointer].options:
                required = modules[pointer].options[option][1]
                if required and modules[pointer].options[option][0] == '':
                    print(f"{bcolors.FAIL}[-]{bcolors.ENDC} Option '{option}' is required but not set.")
                    flag = False
            if flag:
                try:
                    print("Exploiting the module...")
                    if hasattr(modules[pointer], 'exploit'):
                        modules[pointer].exploit()  # Call the exploit method for the module
                    else:
                        print(f"{bcolors.FAIL}[-]{bcolors.ENDC} exploit() method not implemented in the module.")
                except Exception as e:
                    print(f"{bcolors.FAIL}[-]{bcolors.ENDC} An error occurred while exploiting the module: {e}")
					
# Initialization function for loading modules
def init():
    global pluginNumber
    global modules
    plugin_loader = Plugins(modulesPath)
    plugin_loader.crawler()
    plugin_loader.load()
    pluginNumber = len(plugin_loader.pluginTree)
    modules = plugin_loader.modules
    Banner(VERSION, pluginNumber)

# Main loop for reading commands
def mainLoop():
    comp = Completer()
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(comp.complete)
    
    command_instance = Command()  # Create an instance of Command class

    while True:
        command_input = input('ModTester > ').strip().split()  # Renamed 'input' to 'command_input'
        if command_input:
            if command_input[0] in Command.COMMANDS:
                if command_input[0] == "set":
                    command_instance.set(command_input)  # Handle 'set' command
                else:
                    result = getattr(command_instance, command_input[0])(command_input)  # Replaced 'input' with 'command_input'
