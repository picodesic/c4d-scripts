import c4d
from c4d import gui

doc = c4d.documents.GetActiveDocument()
op = doc.GetActiveObject()

atom_radii = {"A": 1.7, "N": 1.54, "C": 1.7, "CA": 1.7, "O": 1.52, "S": 1.85, 
              "H": 1.2, "P": 1.04, "F": 1.47, "Ca": 2.31, "ZN": 1.39}
              

atom_colors = {"A": (0.5, 0.5, 0.5), "N": (0.38, 0.62, 1.0),
               "C": (0.7, 0.7, 0.7), "CA": (0.3, 0.3, 0.3), "O": (0.84, 0.29, 0.29,),
               "S": (0.90, 0.87, 0.32), "H": (1.0, 1.0, 1.0), "P": (1.0, 0.58, 0.0),
               "F": (0.44, 0.89, 0.44), "Ca": (0.58, 0.57, 0.37), "ZN": (0.9, 0.9, 0.9)}

# Metal ions can be identified by residue names. This helps resolve alpha carbon <CA> calcium collision
hetatms = {"CA": "Ca", "ZN": "Zn"}


def atomListfromTag(tag):
    atom_list = []
    full_text = tag[c4d.ANNOTATIONTAG_TEXT]
    lines = [line for line in full_text.splitlines()]
    for line in lines:
        atoms = line.split('|')[4].strip()
        residue = line.split('|')[2].strip()
        het = line.split('|')[0].strip()
        for a in atoms.split(' '):
            if a == 'CA' and residue == 'CA':  # Calcium check
                atom_list.append('Ca')
            elif a in atom_colors.keys():
                # if a == residue:
                #     a = hetatms[residue]  # Use entry from dictionary where element has lowercase 2nd letter
                #     print "Found metal " + a
                atom_list.append(a)
            else:
                atom_list.append(a[0])
    return atom_list


def printResults(num_pts, atom_list, vc_tag):
    data = vc_tag.GetDataAddressR()

    for pnt in xrange(num_pts):
        color = c4d.VertexColorTag.GetPoint(data, None, None, pnt)
        species = atom_list[pnt]

        print pnt, species, color


def tagUpdate(vc_tag, vm_tag, num_pts, atom_list):
    # update vertex color tag with normalized scales in alpha channel of RGBA vector
    data = vc_tag.GetDataAddressW()
    radii = []
    for pnt in xrange(num_pts):
        # Check if double letter name is in dictionary, otherwise use first letter
        # if atom_list[pnt] in atom_colors.keys():
        #     species = atom_list[pnt]
        # else:
        #     species = atom_list[pnt][0]
        # color = atom_colors.get(species, c4d.Vector(0,0,0))
        species = atom_list[pnt]
        color = atom_colors[species]
        if not color:
            print species + " color not found in user data"
            return False
        vc_tag.SetColor(data, None, None, pnt, color)
        size = atom_radii[species] - 1.0  # Account for effector relative scaling
        radii.append(size)
    vm_tag.SetAllHighlevelData(radii)


# Main function
def main():
    if not op:
        gui.MessageDialog('Select object with tag to update.')
        return False
    num_pts = op.GetPointCount()
    if not num_pts:
        gui.MessageDialog('Selected object is not a point object')
        return False
    vc_tag = op.GetTag(c4d.Tvertexcolor)
    if not vc_tag:
        gui.MessageDialog('No vertex color map on object.')
        return False

    tags = op.GetTags()
    for tag in tags:
        if tag[c4d.ID_BASELIST_NAME][-5:] == "sizes":
            vm_tag = tag
    if not vm_tag:
        gui.MessageDialog('No atom size vertex map tag on object.')
        return False
    an_tag = op.GetTag(c4d.Tannotation)
    if not an_tag:
        gui.MessageDialog('No annotation tag on object.')
        return False

    user_data = op.GetUserDataContainer()
    if user_data is None:
        gui.MessageDialog('No User Data present.')
        return False

    for id, bc in user_data:
        if bc[c4d.DESC_PARENTGROUP][-1].id == 2:  # check for Atom Colors parentgroup
            species = bc[1]
            color = op[c4d.ID_USERDATA, id[1].id]
            atom_colors[species] = color
        if bc[c4d.DESC_PARENTGROUP][-1].id == 3:  # check for Atom Sizes parentgroup
            species = bc[1]
            size = op[c4d.ID_USERDATA, id[1].id]
            atom_radii[species] = size

    atom_list = atomListfromTag(an_tag)
    tagUpdate(vc_tag, vm_tag, num_pts, atom_list)
    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
    # printResults(num_pts, atom_list, vc_tag)
    print 'Successfully updated "%s" vertex colors.' % op.GetName()


# Execute main()
if __name__ == '__main__':
    main()