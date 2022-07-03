import c4d
from c4d import gui
from c4d.modules import mograph as mo


doc = c4d.documents.GetActiveDocument()
op = doc.GetActiveObject()


# Main function
def main():
    if not op:
        gui.MessageDialog('Select point cloud object.')
        return False
    pcloud_obj = op
    tags = pcloud_obj.GetTags()
    # print tags
    color_tag = None
    size_tag = None
    for tag in tags:
        if tag[c4d.ID_BASELIST_NAME][-5:] == 'sizes':
            color_tag = tag
        if tag[c4d.ID_BASELIST_NAME][-6:] == 'colors':
            size_tag = tag
    if not color_tag or not size_tag:
        gui.MessageDialog('Needed tags are not present.')
        return False

    atom_cloner = c4d.BaseObject(1018544)
    atom_cloner[c4d.ID_BASELIST_NAME] = 'Atoms'
    atom_cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 0  # Object mode
    atom_cloner[c4d.MGCLONER_VOLUMEINSTANCES_MODE] = 2  # Multi-instance mode
    atom_cloner[c4d.MG_POLY_MODE_] = 0  # Vertex distribution
    atom_cloner[c4d.MG_OBJECT_LINK] = pcloud_obj
    doc.InsertObject(atom_cloner)
    c4d.EventAdd()

    base_sphere = c4d.BaseObject(c4d.Osphere)
    base_sphere[c4d.ID_BASELIST_NAME] = 'base_sphere'
    base_sphere[c4d.PRIM_SPHERE_RAD] = 1
    base_sphere[c4d.PRIM_SPHERE_SUB] = 15
    ph_tag = c4d.BaseTag(c4d.Tphong)
    base_sphere.InsertTag(ph_tag)
    doc.InsertObject(base_sphere, parent=atom_cloner)
    c4d.EventAdd()

    col_size_eff = c4d.BaseObject(1021337)  # Plain effector
    col_size_eff[c4d.ID_BASELIST_NAME] = 'Atom Color, Size'
    col_size_eff[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    col_size_eff[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    col_size_eff[c4d.ID_MG_BASEEFFECTOR_USCALE] = 2.0
    col_size_eff[c4d.ID_MG_BASEEFFECTOR_UNIFORMSCALE] = True

    doc.InsertObject(col_size_eff)
    c4d.EventAdd()

    effector_list = c4d.InExcludeData()
    effector_list.InsertObject(col_size_eff, 1)
    atom_cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = effector_list

    col_size_fields = c4d.FieldList()
    print col_size_fields

    color_layer = mo.FieldLayer(c4d.FLproximity)
    # print color_layer
    print color_layer.GetType()
    color_layer.SetLinkedObject(color_tag)
    color_layer.SetChannelFlag(c4d.FIELDLAYER_CHANNELFLAG_COLOR)
    col_size_fields.InsertLayer(color_layer)

    size_layer = mo.FieldLayer(c4d.FLproximity)
    # print size_layer
    print size_layer.GetType()
    color_layer.SetLinkedObject(size_tag)
    color_layer.SetChannelFlag(c4d.FIELDLAYER_CHANNELFLAG_VALUE)
    col_size_fields.InsertLayer(size_layer)

    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()