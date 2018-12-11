#!/usr/bin/env python3

import subprocess as subp

MAX_LEN_NAME = 19
MAX_LEN_NAME_LEVEL = 23
MAX_LEN_CLASS = 14
MAX_LEN_IP = 15
MAX_LEN_FLAGS = 10
MAX_LEN_PRIV_USED = 5
MAX_LEN_QID = 4

def align(string, limit):
    # aligning needs a monotyped font
    return " " * (limit - len(string))

def assemble_output(domains):
    running = select_domains(domains, 'Running')
    halted = select_domains(domains, 'Halted')
    tree = select_domains(running, 'Tree')

    # Uncomment the following line if you need an unsorted VM list: 
    
    #run = format_output(running, 'Running')
    halt = format_output(halted, 'Halted')
    tree = format_output(tree, 'Tree') 

    print("<txt><span font-family='Consolas'><b>RUNNING</b>\n\n{0}\n<b>HALTED</b>\n\n{1}</span></txt>".format(tree, halt))
    return 0

def colorize_string(string, color, env='gmon'):
    #TODO Add coloring for terminal
    if env == 'gmon':
        return "<span foreground='" + color + "'>" + string + "</span>" 
    else:
        return string

def level_ext(level):
    if level == '-':
        return ""
    elif int(level) == 0:
        return "┌"
    else:
        branch = "{spc}└──".format(spc=("   " * (int(level) - 1)))
        return branch 

def select_domains(domains, state):
    if state == 'Tree':
        parentless_doms = []

        # Split not connected VMs
        #TODO Fix the bug which excludes dom0 from the parnetless list
        for i, vm in enumerate(domains):
            if vm['gateway'] == '-' and 'N' not in vm['flags']:
                parentless_doms.append(vm)
                del domains[i]
        
        tree = parentless_doms
        
        ###
        ### Changing sel_k['***'] to another key will change the order of VMs in the tree.
        ###
        
        domains = sorted(domains, key=lambda sel_k: sel_k['gateway'], reverse=True)
        tree += sort_to_tree(domains, [], '-', 0)
        return tree

    else:
        doms = []
        for vm in domains: 
            if (vm['state'] == state):
               doms.append(vm)
        return doms

def sort_to_tree(domain_ls, tree, parent_gateway, level):
 
    i = 0
    while domain_ls and i < len(domain_ls):
        vm = domain_ls[i]

        # Condition for:
        # Network root VMs (like sys-net)
        if ('-' == vm['gateway'] and 'N' in vm['flags']):
            vm['level'] = level
            tree.append(vm)
            del domain_ls[i]
            i = 0
            sort_to_tree(domain_ls, tree, vm['ip'], level+1)

        # Proxy VMs
        elif (parent_gateway == vm['gateway'] and 'N' in vm['flags']):
            vm['level'] = level
            tree.append(vm)
            del domain_ls[i]
            i = 0
            sort_to_tree(domain_ls, tree, vm['ip'], level+1)

        # Ordinary VMs
        elif (parent_gateway == vm['gateway']):
            vm['level'] = level
            tree.append(vm)
            del domain_ls[i]
            i = 0
        
        else:
            i += 1
    
    # Cancel condition or go level up
    if not domain_ls:
        return tree
    else:
        level -= 1
        return


def parse_domain_ls():
    qvm_ls_fields = ['qid', 'state','label', 'name', 'class', 'netvm', 'ip', 'gateway', 'priv-used', 'template', 'uuid', 'flags', 'level']
    qvm_ls_raw = subp.run(["qvm-ls", "--raw-data", "--fields", ",".join(qvm_ls_fields)], stdout=subp.PIPE).stdout.decode('ascii')

    domain_ls = qvm_ls_raw.splitlines()
    temp_ls = [line.split('|') for line in domain_ls]

    # Each domain is stored as a dictionary. All dicts are stored as list
    domain_dic_ls = [dict(zip(qvm_ls_fields, line)) for line in temp_ls] 
    
    return domain_dic_ls

def format_output(to_print, state):
    #TODO Move formatted_str section into own function.

    ###
    ### Add or remove elements in formatted_str to change the output of the list.
    ###
    

    formatted_str = ''
    if (state == 'Tree'):
        #TODO Print header line 
        for vm in to_print:

            formatted_str += "{level}{name}{a_name}{qclass}{a_qclass}{ip}{a_ip}{used}{a_used}{flags}\n".format(
                    level = colorize_string(level_ext(vm['level']), 'grey', 'gmon'),
                    name = colorize_string(vm['name'], vm['label'], 'gmon'),
                    a_name = align((level_ext(vm['level']) + vm['name']), MAX_LEN_NAME_LEVEL),
                    qclass = vm['class'],
                    a_qclass = align(vm['class'], MAX_LEN_CLASS),
                    ip = vm['ip'],
                    a_ip = align(vm['ip'], MAX_LEN_IP),
                    used = vm['priv-used'],
                    a_used = align(vm['priv-used'], MAX_LEN_PRIV_USED),
                    flags = vm['flags'])
        return formatted_str

    elif (state == 'Running'):

        #sort domain list for specific parameter
        for vm in sorted(to_print, key=lambda sel_k: sel_k['gateway']):

            formatted_str += "{qid}{a_qid}{name}{a_name}{qclass}{a_qlass}{netvm}\n".format(
                    qid = vm['qid'],
                    a_qid = align(vm['qid'], MAX_LEN_QID),
                    name = colorize_string(vm['name'], vm['label'], 'gmon'),
                    a_name = align(vm['name'], MAX_LEN_NAME),
                    qclass = vm['class'],
                    a_qclass = align(vm['class'], MAX_LEN_CLASS),
                    netvm = vm['netvm'])
        return formatted_str

    elif (state == 'Halted'):

        for vm in sorted(to_print, key=lambda sel_k: sel_k['class']):
            formatted_str += "<span foreground='Grey'>{qid}{a_qid}{name}{a_name}{qclass}{a_qclass}{netvm}</span>\n".format(
                    qid = vm['qid'],
                    a_qid = align(vm['qid'], MAX_LEN_QID),
                    name = vm['name'],
                    a_name = align(vm['name'], MAX_LEN_NAME),
                    qclass = vm['class'],
                    a_qclass = align(vm['class'], MAX_LEN_CLASS),
                    netvm = vm['netvm'])
        return formatted_str

if __name__ == "__main__":
    #TODO Add argument parser.
    domains = parse_domain_ls()
    assemble_output(domains)





