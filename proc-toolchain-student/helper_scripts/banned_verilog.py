"""
Checks code for banned Verilog constructs.

@author: Philip Xue
"""

from helper_scripts.logger import Logger
import os
import re
from helper_scripts.default_values import BANNED_VERILOG_TITLE
from helper_scripts.html_generator import HTMLGenerator

'''
# absolutely_banned - these should not be in the code at all

absolutely_banned = ['automatic', 'buf', 'bufif0', 'bufif1', 'cell', 'cmos', 'config', 'deassign', 'defparam', 'design', 'disable', 'endconfig', 'endfunction', 'endprimitive', 'endspecify', 'endtable', 'endtask', 'event', 'force', 'forever', 'fork', 'function', 'highz0', 'highz1', 'ifnone', 'incdir', 'include', 'instance', 'join', 'larger', 'liblist', 'library', 'macromodule', 'medium', 'nmos', 'noshow-cancelled', 'notif0', 'notif1', 'pmos', 'primitive', 'pull0', 'pull1', 'pullup', 'pulldown', 'pulsestyle_ondetect', 'pulsestyle_onevent', 'rcmos', 'real', 'realtime', 'release', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared', 'show-cancelled', 'small', 'specify', 'specpa', 'strong0', 'strong1', 'supply0', 'supply1', 'table', 'task', 'time', 'tran', 'tranif0', 'tranif1', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'use', 'vectored', 'wait', 'wand', 'weak0', 'weak1', 'wor']

# banned - these are banned but also likely to be used
banned = ['always', 'case', 'casex', 'casez', 'default', 'edge', 'else', 'endcase', 'if', 'initial', 'integer', 'negedge', 'posedge', 'reg', 'repeat', 'while']

# pay attention to these ones
attention = ['begin', 'end', 'endgenerate', 'for', 'generate', 'genvar', 'inout', 'input', 'localparam', 'output', 'parameter']
'''

'''
# different levels of regex checking

Ban Level:
1 - Only simple structural verilog
2 - Shift operator is allowed for decoder syntax
3 - In-line gates allowed
4 - Non-behavioral verilog allowed
'''

# matches any of +-*/%&|^~!<>, ==
reg_1 = re.compile('[+\-*/%&|^~!<>]|==')

# matches any of +-*/%&|^~!, >, <, ==, >=, <=
reg_2 = re.compile('[+\-*/%&|^~!]'
                    '|(?<!>)>(?!>)'
                    '|(?<!<)<(?!<)'
                    '|==|>=|<=')

# matches any of +-*/%, >, <, !=, ==, >=, <=
reg_3 = re.compile('[+\-*/%]'
                    '|(?<!>)>(?!>)'
                    '|(?<!<)<(?!<)'
                    '|!=|==|>=|<=')

# matches any of +-*/%, >, <, >=, <=
reg_4 = re.compile('[+\-*/%]'
                    '|(?<!>)>(?!>)'
                    '|(?<!<)<(?!<)'
                    '|>=|<=')
regs = [reg_1, reg_2, reg_3, reg_4]
reg_keyword = re.compile(r'always\s*@'
                    '|always '
                    '|always$'
                    '|case\s*\('
                    '|casex\s*\('
                    '|casez\s*\('
                    '|default\s*:'
                    '|else\s*\('
                    '|else$'
                    '|for\s*\('
                    '|if\s*\('
                    '|if$'
                    '|initial '
                    '|initial$'
                    '|inout\s*\['
                    '|integer '
                    '|reg '
                    '|reg\s*\['
                    '|input reg'
                    '|output reg'
                    '|repeat\('
                    '|while\s*\(')
                    
ignore_list = ("_tb.v", "Wrapper.v", "RAM.v", "ROM.v", "dffe_ref.v")
                    
def check_string(s, level = 1):
    """
    Check if string s starts with a certain set of characters or contains banned constructs based on ban level
    """
    return s.startswith(('`', '$')) or reg_keyword.match(s) or re.search(regs[level-1], s) # or any(s.startswith(item) for item in absolutely_banned)

def get_banned_warning(file_name, lines, type = 'banned', html_friendly = False):
    """
    Returns a warning string for banned Verilog constructs

    type: intro of warning, can be 'banned' or 'generate'
    html_friendly: whether to return a string with HTML tags highlighting important text
    """

    span_start = '<span class="failure">' if html_friendly else ""
    span_end = '</span>' if html_friendly else ""
    message = "Potentially banned syntax" if type == "banned" else "Generate loop(s) detected"
    
    return f'{message} in {span_start}{file_name}{span_end} on the following lines:\n' + '\n'.join(lines) + '\n'

def process_file(f, level = 1):
    """
    Processes a Verilog file and returns a tuple of possible genvar lines and banned lines
    """

    comment_block = False
    generate_block = False
    lines_generate = [[]]
    lines_banned = []
    for i, line in enumerate(f):
        line_nopadding = line.strip()
        stripped = (line_nopadding.partition('//'))[0]
        if not stripped:
            continue

        if stripped.startswith('`timescale') or (comment_block and ('*/' not in stripped)):
            continue
        if '*/' in stripped:
            comment_block = False
            stripped = stripped.partition('*/')[2]
        if stripped.startswith('generate') or (generate_block and not stripped.startswith('endgenerate')):
            generate_block = True
            lines_generate[-1].append((line.rstrip()).replace('\t',"    "))
            continue
        if stripped.startswith('endgenerate'):
            lines_generate[-1].append((line.rstrip()).replace('\t',"    "))
            if len(lines_generate[-1]) > 2:
                lines_generate[-1] = f"{i-len(lines_generate[-1])+1}-{i+1}:\n"+'\n'.join(lines_generate[-1])+'\n'
                lines_generate.append([])
            else:
                lines_generate[-1].clear()
            generate_block = False
        
        if '/*' in stripped:
            comment_block = True
            stripped = stripped.partition('/*')[0]
        if stripped.startswith(('input','output','wire')) and (not reg_keyword.match(stripped)):
            continue
        if check_string(stripped, level):
            line_reformat = (line.rstrip()).replace('\t','    ')
            lines_banned.append(f"{i+1}:\t{line_reformat}")

    # Remove empty list at end of lines_generate
    lines_generate.pop()
    return (lines_generate, lines_banned)

def check_verilog(level = 1, show_generate = True):
    """
    Checks for banned Verilog constructs with varying degrees of strictness
    level 1 - Only simple structural verilog
    level 2 - Shift operator is allowed for decoder syntax
    level 3 - In-line gates allowed
    level 4 - Non-behavioral verilog allowed
    
    Generate loops can be shown using show_generate option
    """
    # Create list of files from FileList.txt
    with open('FileList.txt', 'r', encoding='utf-8') as FileList:
        files = [file.rstrip() for file in FileList]

    failed = False

    # Iterate through files
    for file in files:
        if file.endswith(ignore_list):
            continue

        with open(file, errors='ignore') as f:
            file_name = os.path.basename(file)
            (lines_generate, lines_banned) = process_file(f, level)

            if show_generate and lines_generate:
                Logger.warn(get_banned_warning(file_name, lines_generate, type = 'generate', html_friendly = False))
                HTMLGenerator.add_content(BANNED_VERILOG_TITLE, get_banned_warning(file_name, lines_generate, type = 'generate', html_friendly = True))
                failed = True

            if lines_banned:
                Logger.warn(get_banned_warning(file_name, lines_banned, type = 'banned', html_friendly = False))
                HTMLGenerator.add_content(BANNED_VERILOG_TITLE, get_banned_warning(file_name, lines_banned, type = 'banned', html_friendly = True))
                failed = True

    return failed