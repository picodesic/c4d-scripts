import c4d
from c4d import gui, utils

doc = c4d.documents.GetActiveDocument()
# Create dissacharide chain of user specfied length from selected dissacharide units

# TODO Rewrite using global matrix rather than AbsPos

def main():
    di_unit = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE)
    if not di_unit:
        gui.MessageDialog('Select disaccharides!')
        return False
    chain_length = gui.InputDialog('How many disaccaride units?', 0)
    chain_length = int(chain_length)
    if not chain_length:
        print "No units built."
        return False
    print chain_length
    print di_unit
    s1, s2 = di_unit
    v0 = c4d.Vector(0,0,0)
    v1 = c4d.Vector(0,0,0)
    v2 = s2.GetAbsPos()
    v2_unidir = c4d.Vector(v2[0], 0, 0)
    sac_cloner = c4d.BaseObject(1018544)
    sac_cloner.SetName("Saccharides")
    sac_cloner[c4d.MG_LINEAR_COUNT] = chain_length
    sac_cloner[c4d.MG_LINEAR_OBJECT_POSITION,c4d.VECTOR_X] = v2[0]
    sac_cloner[c4d.MG_LINEAR_OBJECT_POSITION, c4d.VECTOR_Y] = 0
    sac_cloner[c4d.MG_LINEAR_OBJECT_POSITION, c4d.VECTOR_Z] = 0
    sac_cloner[c4d.MG_LINEAR_MODE] = 1  # per step
    doc.InsertObject(sac_cloner)
    s2.InsertUnder(sac_cloner)
    s1.InsertUnder(sac_cloner)
    c4d.EventAdd()
    # sacs = utils.SendModelingCommand(c4d.MCOMMAND_MAKEEDITABLE, list=[sac_cloner], mode=c4d.MODIFY_ALL, doc=doc)
    doc.SetActiveObject(sac_cloner)
    c4d.CallCommand(12236)  # make editable
    sac_null = doc.GetActiveObject()
    sacs = sac_null.GetChildren()

    joint_null = c4d.BaseObject(c4d.Onull)
    joint_null.SetName("Saccharide Joints")
    joint_null.SetAbsPos(sac_null.GetAbsPos())
    doc.InsertObject(joint_null)
    c4d.EventAdd()
    parent_joint = joint_null
    joint_chain = []

    for i in xrange(chain_length):
        j = c4d.BaseObject(c4d.Ojoint)
        sac = sacs[i]
        name = "Joint " + sac.GetName()
        j.SetName(name)
        j.SetAbsPos(v1)
        doc.InsertObject(j, parent=parent_joint)
        psr_tag = c4d.BaseTag(1019364)
        psr_tag[c4d.ID_CA_CONSTRAINT_TAG_PSR] = True
        psr_tag[10001] = j  # set target
        sac.InsertTag(psr_tag)
        parent_joint = j
        v1 = v2
        joint_chain.append(j)
    c4d.EventAdd()

    ik_tag = c4d.BaseTag(1019561)
    ik_tag[c4d.ID_CA_IK_TAG_TIP] = joint_chain[-1]
    ik_tag[c4d.ID_CA_IK_TAG_SOLVER] = 2  # Set to 3D solver
    joint_null.InsertTag(ik_tag)

    ik_spline_tag = c4d.BaseTag(1019862)
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_END] = joint_chain[-1]
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_TYPE] = 0  # None
    ik_spline_tag[c4d.ID_CA_IKSPLINE_TAG_ALIGN_TANGENT] = 0  # align x
    ik_spline_tag[c4d.EXPRESSION_ENABLE] = False
    joint_null.InsertTag(ik_spline_tag)


# Execute main()
if __name__=='__main__':
    main()