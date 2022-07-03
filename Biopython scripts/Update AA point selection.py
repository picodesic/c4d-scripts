import c4d

doc = c4d.documents.GetActiveDocument()
op = doc.GetActiveObject()

res_codes = {'GLY': 'G', 'ALA': 'A', 'VAL': 'V', 'LEU': 'L', 'CYS': 'C', 'MET': 'M', 'PRO': 'P',
             'ILE': 'I', 'SER': 'S', 'THR': 'T', 'TYR': 'Y', 'PHE': 'F', 'ASN': 'N', 'GLN': 'Q',
             'HIS': 'H', 'TRP': 'W', 'ASP': 'D', 'GLU': 'E', 'LYS': 'K', 'ARG': 'R'}

res_sel_atoms = {'A': [], 'C': [], 'E': [], 'D': [], 'G': [], 'F': [], 'I': [], 'H': [], 'K': [], 'M': [],
                'L': [], 'N': [], 'Q': [], 'P': [], 'S': [], 'R': [], 'T': [], 'W': [], 'V': [], 'Y': []}


def updatePoints(obj, ps_tag, an_tag, res_sel_atoms, sel_range):
    count = obj.GetPointCount()
    p_states = [0] * count
    if not clear_all:
        res_list = []
        if len(sel_range) == 0:  # If no range specified in text field
            full_range = True
        else:
            full_range = False
            ranges = sel_range.split(',')
            for r in ranges:
                if '-' in r:
                    lo, hi = r.split('-')
                    for i in xrange(int(lo), int(hi)+1):
                        res_list.append(i)
                else:
                    res_list.append(int(r))

            # print res_list

        full_text = an_tag[c4d.ANNOTATIONTAG_TEXT]
        lines = [line for line in full_text.splitlines()]
        for line in lines:
            r_het, res_num, res_name, atom_indices, atom_names = (i.strip() for i in line.split('|'))
            if r_het == 'A':
                res = res_codes[res_name]
                if len(res_sel_atoms[res]) > 0 or not full_range:
                    rg = [int(r) for r in atom_indices.split('-')]
                    pt_atom = zip(xrange(rg[0], rg[1]+1), atom_names.split(' '))
                    # print pt_atom
                    for a in pt_atom:
                        if specify:
                            if a[1] in res_sel_atoms[res]:
                                if full_range or int(res_num) in res_list:
                                    p_states[a[0]] = 1
                        else:
                            if int(res_num) in res_list:
                                p_states[a[0]] = 1
    # print p_states
    s = ps_tag.GetBaseSelect()
    s.SetAll(p_states)
    print 'Updated point selection tag "%s". Total points: %i' % (ps_tag[c4d.ID_BASELIST_NAME], s.GetCount())
    c4d.EventAdd()


def main():
    ps_tag = doc.GetActiveTag()
    if not ps_tag.IsInstanceOf(c4d.Tpointselection):
        print 'Select AA point selection tag.'
        return False
    obj = ps_tag.GetObject()
    an_tag = obj.GetTag(c4d.Tannotation)
    if not an_tag:
        print 'No annotation tag found.'
        return False
    # residues = residuesFromTag(an_tag)
    user_data = ps_tag.GetUserDataContainer()
    if user_data is None:
        gui.MessageDialog('No User Data present.')
        return False

    # parent = ''
    sel_range = ''
    select_all = False
    global specify
    specify = True
    global clear_all
    clear_all = False
    for id, bc in user_data:
        # print("User Data ID: " + str(id))
        if id[1].dtype == c4d.DTYPE_STRING:
            sel_range = ps_tag[id]
        elif id[1].dtype == c4d.DTYPE_GROUP:
            aa = bc[c4d.DESC_NAME][-2]  # Get single letter aa code from end of name
            select_all = False
        elif id[1].dtype == c4d.DTYPE_BOOL:
            name = bc[c4d.DESC_NAME]
            if name == 'Clear All':
                if ps_tag[id] == True:
                    clear_all = True
                    ps_tag[id] = False
            elif name == 'Specify below' and ps_tag[id] == False:
                specify = False
            elif clear_all and name != 'Specify below': #  TODO figure out how to check parentgroup instead
                ps_tag[id] = False
            elif name == 'All' and ps_tag[id] == True:
                select_all = True
                # parent = bc[c4d.DESC_PARENTGROUP]
            elif name != 'Specify below':
                if select_all == True:
                    ps_tag[id] = True
                    res_sel_atoms[aa].append(name)
                elif ps_tag[id] == True:
                    res_sel_atoms[aa].append(name)
        # print("User Data Value: " + str(ps_tag[id]))
        # print("User Data Name: " + bc[c4d.DESC_NAME])
    c4d.EventAdd()
    # print res_sel_atoms
    updatePoints(obj, ps_tag, an_tag, res_sel_atoms, sel_range)

# Execute main()
if __name__=='__main__':
    main()