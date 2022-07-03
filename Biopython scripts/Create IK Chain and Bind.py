import c4d
from c4d import gui

standard_aa_names = ["ALA", "CYS", "ASP", "GLU", "PHE", "GLY", "HIS", "ILE", "LYS",
                     "LEU", "MET", "ASN", "PRO", "GLN", "ARG", "SER", "THR", "VAL",
                     "TRP", "TYR"]

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


def makeJoints(obj, residues):
    if obj.GetName()[-6:] != 'pcloud':
        go_ahead = gui.QuestionDialog("Object name does not end in 'pcloud'. Continue?")
        if not go_ahead:
            print 'Ik chain creation cancelled.'
            exit()
    root_name = obj.GetName()[:-7]
    spline_name = root_name + ' backbone'
    spline_obj = doc.SearchObject(spline_name)
    if not spline_obj:
        gui.MessageDialog('Spline backbone object not present, or point cloud object does not follow "* pcloud" naming convention.')
        return False
    print "Creating joints based on '%s'" % spline_obj.GetName()
    # doc.SetActiveObject(spline_obj, mode=c4d.SELECTION_NEW)
    # c4d.CallCommand(1019950, 1019950) # Spline to Joints (limited to 100 joints)
    def setJointPositionFromSplinePoint(joint, spline_pts, id):
        p_offset = spline_pts[id]
        sp_Mg = spline_obj.GetMg()
        pt_Mg = c4d.Matrix()
        pt_Mg.off = p_offset
        pt_Mg = sp_Mg * pt_Mg
        joint.SetMg(pt_Mg)

    spline_pts = spline_obj.GetAllPoints()
    joint_0 = c4d.BaseObject(c4d.Ojoint)
    setJointPositionFromSplinePoint(joint_0, spline_pts, 0)
    doc.InsertObject(joint_0)
    prev_joint = joint_0
    for i in xrange(1, len(spline_pts)):
        joint = c4d.BaseObject(c4d.Ojoint)
        joint.InsertUnder(prev_joint)
        setJointPositionFromSplinePoint(joint, spline_pts, i)
        prev_joint = joint

    c4d.EventAdd()
    # joint_0 = doc.GetFirstObject()
    # if joint_0.GetName != 'Joint':
    #     gui.MessageDialog('Joint chain not created successfully.')
    #     return False
    joint_chain = []
    current_joint = joint_0
    # print len(residues)
    for j in xrange(len(residues)):
        joint_name = root_name + '.' + residues[j][0] + '.' + residues[j][1]
        # print joint_name
        current_joint.SetName(joint_name)
        joint_chain.append(current_joint)
        next_joint = current_joint.GetDown()
        current_joint = next_joint
    # Add IK tag to joint head
    ik_tag = c4d.BaseTag(1019561)
    # ik_tag[c4d.EXPRESSION_ENABLE] = False
    ik_spline_tag = c4d.BaseTag(1019862)
    # ik_spline_tag[c4d.EXPRESSION_ENABLE] = False
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_END] = joint_chain[-1]
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_TYPE] = 0  # None
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_SPLINE] = spline_obj
    ik_tag[c4d.ID_CA_IK_TAG_TIP] = joint_chain[-1]
    ik_tag[c4d.ID_CA_IK_TAG_SOLVER] = 2  # Set to 3D solver
    joint_chain[0].InsertTag(ik_spline_tag)
    joint_chain[0].InsertTag(ik_tag)
    print "Added joint chain containing %i joints with IK tag and IK-Spline tag" % len(joint_chain)

    return joint_chain


def weightTag(obj, joints, residues):
    root_name = obj.GetName()[:-7]
    w_tag = c4d.BaseTag(c4d.Tweights)
    w_tag[c4d.ID_BASELIST_NAME] = root_name + ' weights'
    obj.InsertTag(w_tag)
    # print len(residues)
    for i in xrange(len(residues)):
        # print i
        joint = joints[i]
        # print joint
        j = w_tag.AddJoint(joint)
        # print j
        # print w_tag.GetJointCount()
        start_pt, end_pt = (int(p) for p in residues[i][2].split('-'))
        # print start_pt, end_pt
        for pt in xrange(start_pt, end_pt + 1):
            w_tag.SetWeight(j, pt, 1.0)
    c4d.EventAdd()
    print "Created weight tag and skin deformer for '%s'" % obj.GetName()



# Main function
def main():
    if not op:
        gui.MessageDialog('Select point cloud object with an annotation tag present.')
        return False
    pcloud_obj = op
    an_tag = op.GetTag(c4d.Tannotation)
    if not an_tag:
        gui.MessageDialog('No annotation tag on object.')
        return False
    residues = residuesFromTag(an_tag)
    # TODO: Get points list from residues
    joint_chain = makeJoints(pcloud_obj, residues)
    weightTag(pcloud_obj, joint_chain, residues)
    skin_deform = c4d.BaseObject(1019363)
    doc.InsertObject(skin_deform, parent=pcloud_obj)
    # print joint_chain



# Execute main()
if __name__=='__main__':
    main()