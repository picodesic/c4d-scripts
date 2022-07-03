import c4d

doc = c4d.documents.GetActiveDocument()
op = doc.GetActiveObject()


def residuesFromTag(tag):
    residues = []
    full_text = tag[c4d.ANNOTATIONTAG_TEXT]
    lines = [line for line in full_text.splitlines()]
    for line in lines:
        r_het, res_num, res_name, atom_indices, atom_names = (i.strip() for i in line.split('|'))
        if r_het == 'A':
            residues.append((res_num, res_name, atom_indices, atom_names))
    # print residues
    return residues


def buildSpline(obj, residues):
    # Get alpha carbon list
    m = obj.GetMg()
    alpha_carbons = []
    start_index = int(residues[0][2].split('-')[0])
    print start_index
    for res in residues:
        verts = res[2]
        id = int(verts.split('-')[0]) + 1 - start_index  # CA atom minus start
        vec = obj.GetPoint(id)
        alpha_carbons.append(vec)
    # print alpha_carbons
    print 'Backbones splines thread through alpha carbons of amino acid residues.'

    # print backbone_atoms
    pnts = len(alpha_carbons)
    # Initialize spline object
    spline = c4d.SplineObject(pnts, c4d.SPLINETYPE_CUBIC)
    spline_name = obj.GetName()[:-6] + 'backbone'
    spline.SetName(spline_name)
    # Set color to bright green
    spline[c4d.ID_BASEOBJECT_USECOLOR] = 1
    spline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0.3, 1, 0.42)

    for id in xrange(pnts):
        spline.SetPoint(id, alpha_carbons[id])
    spline.Message(c4d.MSG_UPDATE)
    doc.InsertObject(spline)
    spline.SetMg(m)
    c4d.EventAdd()
    print 'Added spline object "%s" consisting of points located at alpha-carbon position of each residue' % spline_name
    return spline


def main():
    if op is None:
        print 'No object selected.'
        return False
    obj = op
    an_tag = obj.GetTag(c4d.Tannotation)
    if not an_tag:
        print 'No annotation tag found.'
        return False
    residues = residuesFromTag(an_tag)
    spline = buildSpline(obj, residues)


# Execute main()
if __name__=='__main__':
    main()