#!/usr/bin/env python3

import subprocess as subp

def align(string, limit):
    # aligning needs a monotyped font
    return " " * (limit - len(string))

def assemble_output(domains):
    running = select_domains(domains, 'Running') #list_running(domains)
    halted = select_domains(domains, 'Halted')
    tree = select_domains(running, 'Tree')  #print_tree(running)

    # -> Unsorted VM list: run = print_standard_ls(running, 'Running')
    halt = print_standard_ls(halted, 'Halted')
    tree = print_standard_ls(tree, 'Tree') 

    print("<txt><span font-family='Consolas'><b>RUNNING</b>\n\n{0}\n<b>HALTED</b>\n\n{1}</span></txt>".format(tree, halt))
    return 0

def colorize_string(string, color, env='gmon'):
    # This function colors a string for gmon.
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
        branch = "{spc}└──".format(spc=("   " * (int(level) - 1)))   #¦
        return branch 

def select_domains(domains, state):
    if state == 'Tree':
        parentless_doms = []

        # Split not connected VMs
        for i, vm in enumerate(domains):
            print(vm['name'],vm['flags'],vm['gateway'])
            if vm['gateway'] == '-' and 'N' not in vm['flags']:
                parentless_doms.append(vm)
                del domains[i]
        
        tree = parentless_doms
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

    # Per list vm we have one domain with all its fields.
    domain_ls = qvm_ls_raw.splitlines()
    temp_ls = [line.split('|') for line in domain_ls]

    # Each domain is stored as a dictionary. All dicts are stored as list
    domain_dic_ls = [dict(zip(qvm_ls_fields, line)) for line in temp_ls] 
    
    return domain_dic_ls

def print_standard_ls(to_print, state):
    #TODO write format_string function
    #TODO Remove magic numbers in align()
    formatted_str = ''
    if (state == 'Tree'):
        #TODO Print header line 
        for vm in to_print:

            formatted_str += "{level}{name}{align0}{qclass}{align1}{ip}{align2}{used}{align3}{flags}\n".format(
                    level = colorize_string(level_ext(vm['level']), 'grey', 'gmon'),
                    name = colorize_string(vm['name'], vm['label'], 'gmon'),
                    align0 = align((level_ext(vm['level']) + vm['name']), 23),
                    qclass = vm['class'],
                    align1 = align(vm['class'], 14),
                    ip = vm['ip'],
                    align2 = align(vm['ip'], 14),
                    used = vm['priv-used'],
                    align3 = align(vm['priv-used'], 5),
                    flags = vm['flags'])
        return formatted_str

    elif (state == 'Running'):

        #sort domain list for specific parameter
        for vm in sorted(to_print, key=lambda sel_k: sel_k['gateway']):

            formatted_str += "{qid}{align0}{name}{align1}{qclass}{align2}{netvm}\n".format(
                    qid = vm['qid'],
                    align0 = align(vm['qid'], 4),
                    name = colorize_string(vm['name'], vm['label'], 'gmon'),
                    align1 = align(vm['name'], 19),
                    qclass = vm['class'],
                    align2 = align(vm['class'], 14),
                    netvm = vm['netvm'])
        return formatted_str

    elif (state == 'Halted'):

        for vm in sorted(to_print, key=lambda sel_k: sel_k['class']):
            formatted_str += "<span foreground='Grey'>{0}{1}{2}{3}{4}{5}{6}</span>\n".format(
                    vm['qid'],
                    align(vm['qid'], 4),
                    vm['name'],
                    align(vm['name'], 19),
                    vm['class'],
                    align(vm['class'], 14),
                    vm['netvm'])
        return formatted_str

if __name__ == "__main__":
    #TODO Add argument parser.
    domains = parse_domain_ls()
    assemble_output(domains)






