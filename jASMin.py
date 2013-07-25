#!/usr/bin/python

'''
TODO:
    Implement HEX->ASM
'''

import os
import sys
import cmd
import subprocess
import platform
import select
import re
import time
import shlex

class processASM():

    def __init__(self, arg, mode, format):

        self.dir = os.path.dirname(os.path.realpath(__file__))

        # Assembly file template
        asmtxt = '''
            .text
            _start:
            .global _main
            main:
                xxx
            .end
        '''

        # Place arg into file and split by ;
        if mode == "ARM":
            asmtxt = asmtxt.replace("xxx", arg.replace(";", "\n"))
        else:
            asmtxt = asmtxt.replace("xxx", ".code   16\n" + arg.replace(";", "\n")) # .code 16 puts it into THUMB mode

        # Write to file
        f = open(self.dir + "/tmp.asm", "w")
        f.write(asmtxt)
        f.close()

        # Assemble + disassemble
        asm = subprocess.Popen(self.dir + "/arm-linux-androideabi-as tmp.asm -o tmp.out", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        asm.wait()
        disasm = subprocess.Popen(self.dir + "/arm-linux-androideabi-objdump -d tmp.out", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        disasm.wait()

        # Only parse from line with "0:"
        foundZeroColon = False
        output = ""
        for line in disasm.stdout.readlines():
            if "0:" in line:
                foundZeroColon = True

            if foundZeroColon and ":" in line:
                matchObj = re.match( r'.*:\s*([a-fA-F0-9]*)\s*.*', line, re.M|re.I)
                line = matchObj.group(1)

                try:
                    if (line[6:8].strip() != ""):
                        output += self._outputStyle(line[6:8], format)
                except:
                    pass

                try:
                    if (line[4:6].strip() != ""):
                        output += self._outputStyle(line[4:6], format)
                except:
                    pass

                output += self._outputStyle(line[2:4], format)
                output += self._outputStyle(line[0:2], format)

        if not foundZeroColon:
            print "Invalid instruction(s)"
        else:
            print output.strip().strip(",")

        # Cleanup
        try:
            os.remove(self.dir + "/tmp.asm")
        except OSError:
            pass

        try:
            os.remove(self.dir + "/tmp.out")
        except OSError:
            pass

    # Format the output
    def _outputStyle(self, arg, format):
        if format == "ARRAY":
            return "0x" + arg + ", "
        else:
            return "\\x" + arg

class jASMin(cmd.Cmd):
    
    mode = "ARM"
    format = "ARRAY"
    direction = "ASM->HEX"
    prompt = '> '
    doc_header = "Commands (type help <command>)"
    intro = '''
    _   _   ___ __  __ _      
   (_) /_\ / __|  \/  (_)_ _  
   | |/ _ \\\\__ \ |\/| | | ' \\ 
  _/ /_/ \_\___/_|  |_|_|_||_|
 |__/                                                                                                                                                          
     twist your droid's ARM

Type 'help' or '?' to list commands
Separate instructions by ;

[mode]      %s
[format]    %s
[direction] %s
''' % (mode, format, direction)

    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_config(self, arg):
        'Print the current status of the console configuration'
        print '''
[mode]      %s
[format]    %s
[direction] %s
''' % (self.mode, self.format, self.direction)

    def do_mode(self, arg):
        'Change modes between ARM and THUMB'
        if self.mode == "ARM":
            self.mode = "THUMB"
        else:
            self.mode = "ARM"
        print "[mode]      " + self.mode

    def do_format(self, arg):
        'Change output formats between ARRAY and HEXSTR'
        if self.format == "ARRAY":
            self.format = "HEXSTR"
        else:
            self.format = "ARRAY"
        print "[format]    " + self.format

    def do_direction(self, arg):
        'Change direction between ASM->HEX and HEX->ASM'
        if self.direction == "ASM->HEX":
            #self.direction = "HEX->ASM"
            print "HEX->ASM not yet implemented :("
        else:
            #self.direction = "ASM->HEX"
            pass
        print "[direction] " + self.direction

    def do_load(self, arg):
        'Load the contents of a file and convert'

        if len(arg) > 0:
            try:
                f = open(arg, 'r')
                contents = f.read()
                f.close()
                processASM(contents, self.mode, self.format)
            except:
                print "Invalid file"
        else:
            print "Enter path to file"

    def complete_load(self, text, line, begidx, endidx):

        splitargs = shlex.split(line)

        if (len(splitargs) == 2):
            enteredpath = splitargs[1]

        folder = enteredpath[:enteredpath.rfind('/') + 1] if (enteredpath != '/') else "/"
        halfcomplete = enteredpath[enteredpath.rfind('/') + 1:]

        return [
                ((path + "/") if os.path.isdir(folder + path) else (path)) for path in os.listdir(folder)
                if (path.startswith(halfcomplete) and path != halfcomplete)
            ]

    def do_exit(self, arg):
        'Exit'
        return True

    def help_help(self):
        print "Initiating data wipe..."
        print "$ rm -rf /home"
        time.sleep(3)
        print "Just kidding :D What are you doing though? Asking for help on help..."

    def help_cpu_modes(self):
        print '''
To change between ARM and THUMB mode, simply type `mode`

To change mid instruction sequence between ARM and THUMB use `.code 32` and `.code 16` respectively
For example, the following uses ARM first and then switches to THUMB:
    > mov r0, r1; .code 16; mov r1, r2; mov r2, r3
    0x01, 0x00, 0xa0, 0xe1, 0x11, 0x1c, 0x1a, 0x1c

If you have no idea what any of this is then I suggest you do some googling :)
    '''

    def help_instruction_reference(self):
        print '''
  ARM: http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0068b/CIHEDHIF.html
THUMB: http://infocenter.arm.com/help/topic/com.arm.doc.dui0068b/BABJHFEA.html
    '''

    def default(self, arg):
        processASM(arg, self.mode, self.format)

if __name__ == '__main__':

    # System check
    if platform.system() != "Linux":
        print "Sorry, Linux only :P"
    else:
        jASMin().cmdloop()
