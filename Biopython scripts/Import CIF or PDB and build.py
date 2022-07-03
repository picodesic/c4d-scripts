import c4d
from c4d import gui, storage
import os
from pprint import pprint
from Bio.PDB import *

doc = c4d.documents.GetActiveDocument()
op = doc.GetActiveObject()

# debug path = "E:\\Dropbox\\Sci Viz\\BioVisualization\\Doodles\\cif"

atom_radii = {"A": 1.7, "N": 1.54, "C": 1.7, "CA": 1.7, "O": 1.52, "S": 1.85,
              "H": 1.2, "P": 1.04, "F": 1.47, "Ca": 2.31, "ZN": 1.39}

atom_colors = {"A": (0.5, 0.5, 0.5), "N": (0.38, 0.62, 1.0),
               "C": (0.7, 0.7, 0.7), "CA": (0.3, 0.3, 0.3), "O": (0.84, 0.29, 0.29,),
               "S": (0.90, 0.87, 0.32), "H": (1.0, 1.0, 1.0), "P": (1.0, 0.58, 0.0),
               "F": (0.44, 0.89, 0.44), "Ca": (0.58, 0.57, 0.37), "ZN": (0.9, 0.9, 0.9)}

standard_aa_names = ["ALA", "CYS", "ASP", "GLU", "PHE", "GLY", "HIS", "ILE", "LYS",
                     "LEU", "MET", "ASN", "PRO", "GLN", "ARG", "SER", "THR", "VAL",
                     "TRP", "TYR"]
# preset booleans:
global nucleic_acid
nucleic_acid = False


#------- User Data
def createUserDataGroup(obj, name, parentGroup=None, columns=None, shortname=None):
    if obj is None: return False
    if shortname is None: shortname = name
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = shortname
    bc[c4d.DESC_TITLEBAR] = 1
    bc[c4d.DESC_DEFAULT] = 1
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    if columns is not None:
        bc[22] = columns

    return obj.AddUserData(bc)

def addColorUserData(obj, atom, c, parent_group):
    color = c4d.Vector(*c)
    bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_COLOR)  # Create default container
    bc[c4d.DESC_NAME] = atom
    bc[c4d.DESC_SHORT_NAME] = atom
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    bc[c4d.DESC_PARENTGROUP] = parent_group
    bc[c4d.DESC_DEFAULT] = color
    element = obj.AddUserData(bc)
    obj[element] = color
    return element

def addSizeUserData(obj, atom, r, parent_group):
    bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_REAL)
    bc[c4d.DESC_NAME] = atom
    bc[c4d.DESC_SHORT_NAME] = atom
    bc[c4d.DESC_STEP] = 0.01
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    bc[c4d.DESC_PARENTGROUP] = parent_group
    bc[c4d.DESC_DEFAULT] = r
    element = obj.AddUserData(bc)
    obj[element] = r
    return element

def addSwitchUserData(obj, name, state, parent_group):
    bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BOOL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    bc[c4d.DESC_PARENTGROUP] = parent_group
    bc[c4d.DESC_DEFAULT] = state
    element = obj.AddUserData(bc)
    obj[element] = state
    return element

#------- End User Data

def pointcloud(name, atoms):
    # populate point list from atom coordinates
    # The import is resulting in mirror flipped structures. Will have to adjust and invert one axis
    point_list = [a.get_coord() for a in atoms]
    pnts = len(point_list)
    # Initialize object
    obj = c4d.PolygonObject(pnts, 0)
    obj_name = str(name) + ' pcloud'
    obj.SetName(obj_name)

    # Create pointcloud
    for id in xrange(pnts):
        v = [f.item() for f in point_list[id]]  # Convert numpy float to native float
        # p = c4d.Vector(*v)  # unpack list of coordinates into vector
        p = c4d.Vector(v[0], v[1], -v[2])  # Adjust for axis flipping
        obj.SetPoint(id, p)
    obj.Message(c4d.MSG_UPDATE)
    # Add object to scene
    doc.InsertObject(obj)
    c4d.EventAdd()
    print 'Added polygon object consisting only of points for atom positions: "%s"' % obj_name
    return obj


def buildSpline(name, atoms):
    # Get alpha carbon list
    if nucleic_acid:
        phosphates = [a.get_coord() for a in atoms if a.get_name() == 'P']
        backbone_atoms = phosphates
        print 'Backbones splines thread through phosphates.'

    else:
        # ca_atoms = [a for a in atoms if a.get_fullname() == ' CA '] #  for some reason FastMMCIF doesn't return spaces
        ca_atoms = [a for a in atoms if a.get_name() == 'CA']
        alpha_carbons = []
        # Calcium atom check
        for a in ca_atoms:
            if a.get_parent().get_resname() == 'CA':
                continue
            elif a.get_fullname() == 'CA  ':
                continue
            else:
                alpha_carbons.append(a.get_coord())
        backbone_atoms = alpha_carbons
        print 'Backbones splines thread through alpha carbons of amino acid residues.'

    # print backbone_atoms
    pnts = len(backbone_atoms)
    # Initialize spline object
    spline = c4d.SplineObject(pnts, c4d.SPLINETYPE_CUBIC)
    spline_name = name + ' backbone'
    spline.SetName(spline_name)
    # Set color to bright green
    spline[c4d.ID_BASEOBJECT_USECOLOR] = 1
    spline[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0.3, 1, 0.42)

    for id in xrange(pnts):
        v = [f.item() for f in backbone_atoms[id]]  # Convert numpy float to native float
        # p = c4d.Vector(*v)  # unpack list of coordinates into vector
        p = c4d.Vector(v[0], v[1], -v[2])  # Adjust for axis flipping
        spline.SetPoint(id, p)
    spline.Message(c4d.MSG_UPDATE)
    doc.InsertObject(spline)
    c4d.EventAdd()
    print 'Added spline object "%s" consisting of points located at alpha-carbon position of each residue' % spline_name
    return spline


def annotationTag(obj, name, res_entries):
    readable_entries = []
    for entry in res_entries:
        r_het, r_num, r_name, atom_index_range, res_atoms = entry
        readable_entry = '%s | %i | %s | %i-%i | %s' % (r_het, r_num, r_name, atom_index_range[0], atom_index_range[1],
                                                      ' '.join(res_atoms))
        readable_entries.append(readable_entry)
    anTag = c4d.BaseTag(c4d.Tannotation)
    anTag[c4d.ID_BASELIST_NAME] = name
    anTag[c4d.ANNOTATIONTAG_TEXT] = '\n'.join(readable_entries)
    anTag[c4d.ANNOTATIONTAG_VIEWPORT_SHOW] = 0
    obj.InsertTag(anTag)
    c4d.EventAdd()
    print 'Added annotation tag with full residue:atom list to "%s"' % (obj.GetName())


def bfactorTag(obj, name, atoms):
    bfactor_list = [a.get_bfactor()/100 for a in atoms]  # Divide by 100 to adjust for vertex map percent basis
    num = len(bfactor_list)
    # bmax = max(bfactor_list)
    # bfactor_norm = [b/bmax for b in bfactor_list]
    # Normalization is unnecessary if tag values are unclamped in atom size effector
    bf_tag = c4d.VariableTag(c4d.Tvertexmap, num)
    bf_tag[c4d.ID_BASELIST_NAME] = name + ' temperature (B-factor)'
    bf_tag.SetAllHighlevelData(bfactor_list)

    obj.InsertTag(bf_tag)
    c4d.EventAdd()
    print 'Added B-Factor (temperature factor) values to vertex map tag to "%s"' % (obj.GetName())
    return bf_tag

def pointSelectionTags(obj, name, atoms):

    def insertPSTag(list_name, p_states):
        # print list_name, p_states
        ps_tag = c4d.SelectionTag(c4d.Tpointselection)
        ps_tag.SetName(name + '_' + list_name)
        obj.InsertTag(ps_tag)
        s = ps_tag.GetBaseSelect()
        s.SetAll(p_states)
        print 'Added point selection tag "%s". Total points: %i' % (list_name, s.GetCount())
        c4d.EventAdd()

    print 'Total atoms in chain %s: %i' % (name, len(atoms))
    rs_dict = {'aa': []}
    # build dictionary keys
    for a in atoms:
        key = a.get_parent().get_resname()
        if key not in rs_dict:
            rs_dict[key] = []
    # populate all residue lists with booleans
    # print rs_dict
    for a in atoms:
        for key in rs_dict:
            if key != 'aa':
                if a.get_parent().get_resname() == key:
                    rs_dict[key].append(1)
                else:
                    rs_dict[key].append(0)
        # check if atom is in standard amino acids
        if is_aa(a.get_parent()):
            rs_dict['aa'].append(1)
        else:
            rs_dict['aa'].append(0)

    if nucleic_acid:
        for list_name, p_states in rs_dict.iteritems():
            if list_name != 'aa':
                insertPSTag(list_name, p_states)
    else:
        # Do not include point selection tag for every aa residue
        for list_name, p_states in rs_dict.iteritems():
            if list_name not in standard_aa_names:
                insertPSTag(list_name, p_states)


def makeVertexTags(obj, name, atoms, atom_colors, atom_radii):
    # norm_factor = 2
    num_pts = obj.GetPointCount()
    vm_tag = c4d.VariableTag(c4d.Tvertexmap, num_pts)  # This new tag is for radius values
    vm_tag[c4d.ID_BASELIST_NAME] = name + ' atom sizes'
    vc_tag = c4d.VertexColorTag(num_pts)
    vc_tag[c4d.ID_BASELIST_NAME] = name + ' atom colors'
    # Make points visible
    vc_tag[c4d.ID_VERTEXCOLOR_DRAWPOINTS] = True
    vc_data = vc_tag.GetDataAddressW()
    radii =[]

    uncolored = []
    for pnt in xrange(num_pts):
        species = atoms[pnt].get_name()
        # print species
        # lookup color, radius from dict or return default
        # Calcium check for confusion with alpha carbons
        if species == 'CA':
            if atoms[pnt].get_fullname() == 'CA  ' or atoms[pnt].get_parent().get_resname == 'CA':
                # gui.MessageDialog('This protein may contain calcium. Fix the script.')
                # color = (0,0,0)
                species = 'Ca'
            # Calcium atoms are usually within residues named 'CA'
            # elif atoms[pnt].get_parent().get_resname == 'CA':
            #     # color = (0,0,0)
            #     species = 'Ca'
            # else:  # we have an alpha carbon
            #     color = atom_colors.get(species, (0, 0, 0))
            #     # radius = atom_radii.get(species, 1.0) / norm_factor
            #     # Normalization unnecessary if tag values in atom color effector are unclamped
            #     radius = atom_radii.get(species, 1.0)
        # else:
        # if atoms[pnt].get_parent().get_id()[0][0] != ' ' and species in atom_colors.keys(): # Check if not aa
        if species in atom_colors.keys():
            color = atom_colors.get(species, (0,0,0))  # Use first letter only for dict retrieval
            radius = atom_radii.get(species, 1.0) - 1.0  # Account for effector relative scaling

        else:
            color = atom_colors.get(species[0], (0,0,0))
            radius = atom_radii.get(species[0], 1.0) - 1.0  # Account for effector relative scaling
        # Check if atoms were retrieved that are not defined in color, size dictionaries
        if color == (0,0,0) and species not in uncolored:
            uncolored.append(species)
        # radius = atom_radii.get(species[0], 1.0) / norm_factor
        radii.append(radius)
        vc_tag.SetColor(vc_data, None, None, pnt, color)
        vc_tag.SetAlpha(vc_data, None, None, pnt, 1.0)
    # Split out vertex color alpha, which contained radius values to its own vertex map
    vm_tag.SetAllHighlevelData(radii)

    obj.InsertTag(vc_tag)
    obj.InsertTag(vm_tag)
    c4d.EventAdd()
    if uncolored:
        uncolored_error = 'WARNING: These species have undefined colors and/or sizes: ' + ', '.join(uncolored)
        print name + ': ' + uncolored_error
        gui.MessageDialog(name + ': ' + uncolored_error)
    print 'Added vertex color tag and vertex map tag (for atom sizes) to "%s"' % (obj.GetName())
    return vc_tag, vm_tag


def residueEntries(chain):
    res_entries = []
    # chain_num = 0
    atom_index_start = 0
    for res in chain.get_residues():
        # r_het = res.get_id()[0][0]
        if res.get_id()[0] == ' ':
            r_het = 'A'
        else:
            r_het = res.get_id()[0][0]
        r_num = res.get_id()[1]
        r_name = res.get_resname()
        res_atoms = [a.get_name() for a in res.get_atoms()]
        atom_index_end = atom_index_start + len(res_atoms) - 1
        atom_index_range = atom_index_start, atom_index_end
        res_entry = (r_het, r_num, r_name, atom_index_range, res_atoms)
        res_entries.append(res_entry)
        atom_index_start = atom_index_end + 1

    return res_entries


def multiObjects(structure):
    def multi_warning(warning_type):
        warning = 'WARNING: Multiple %s present. ' \
                  'Point clouds and splines will be split into separate objects for each chain. ' % warning_type
        gui.MessageDialog(warning)
        print warning
    multi_model = False
    multi_chain = False
    model_num = 0
    chain_num = 0
    for model in structure.get_list():
        model_num += 1
        if model_num == 2:
            multi_model = True
            multi_warning('models')
        for chain in model.get_list():
            chain_num += 1
            if chain_num == 2:
                multi_chain = True
                multi_warning('chains')

    return multi_model, multi_chain


def getOperations():
    options = []
    do_all = False
    do_all = gui.QuestionDialog('Perform all operations? Select No to specify options.')
    if do_all:
        operations = do_all, options
        return operations
    print "Operations --\nPC: point cloud, SP: alpha-carbon backbone spline, AT: annotation tag,\n" \
          "PS: Point Selections, VC: vertex color tag with alpha for size, BF: B-Factor (temperature) tag,\n" \
          "UD: user data for atom color, size"
    ops = ('PC', 'SP', 'AT', 'PS', 'VC', 'BF', 'UD')
    text = 'Input: ' + ', '.join(ops)
    selected = gui.InputDialog(text)
    # print selected
    for s in ops:
        if s in selected.upper():
            options.append(s)
    if options:
        print 'Selected operations: ' + ', '.join(options)
    else:
        print 'No operations selected.'
        # gui.MessageDialog('No operations selected.')
    operations = do_all, options
    return operations


def checkPath():
    path = doc.GetDocumentPath()
    if not path:
        gui.MessageDialog('Save the project first. A new ./cif subdirectory will be created.')
        print 'File save needed before performing requested operation.'
        return False
    return path


def doOperations(operations, chain_name, chain, atoms):
    # React to user requests for operations on protein data
    do_all, options = operations
    if do_all or 'SP' in options:
        if op and op.IsInstanceOf(c4d.Opoint):  # Work on existent point cloud
            obj = op
        spline = buildSpline(chain_name, atoms)
    if do_all or 'PC' in options:
        obj = pointcloud(chain_name, atoms)
    # if not simple_struct:
    if do_all or 'PS' in options:
        pointSelectionTags(obj, chain_name, atoms)
    if do_all or 'AT' in options:
        res_entries = residueEntries(chain)
        annotationTag(obj, chain_name, res_entries)
    if do_all or 'VC' in options:
        vc_tag, vm_tag = makeVertexTags(obj, chain_name, atoms, atom_colors, atom_radii)
    if do_all or 'BF' in options:
        if atoms[0].get_bfactor() and not nucleic_acid:
            if op and op.IsInstanceOf(c4d.Opoint):  # Trying to get a b-factor tag on existent pcloud
                obj = op
            bf_tag = bfactorTag(obj, chain_name, atoms)
        else:
            print 'No meaningful B-Factor information available. Skipping tag creation.'
    # Create User Data:
    if do_all or 'UD' in options:
        atom_details_group = createUserDataGroup(obj, "Atom Details", c4d.DescID(0))
        atom_colors_group = createUserDataGroup(obj, "Atom Colors", atom_details_group, columns=3)
        atom_size_group = createUserDataGroup(obj, "Atom Size", atom_details_group, columns=3)
        # reset_group = createUserDataGroup(obj, "Reset", atom_details_group, columns=2)
        # addSwitchUserData(obj, 'Reset Colors', False, reset_group)
        # addSwitchUserData(obj, 'Reset Sizes', False, reset_group)

        for atom, color in atom_colors.iteritems():
            addColorUserData(obj, atom, color, atom_colors_group)
        print 'Added User Data for atom species colors to "%s"' % (obj.GetName())

        for atom, radii in atom_radii.iteritems():
            addSizeUserData(obj, atom, radii, atom_size_group)
        print 'Added User Data for atom species sizes to "%s"' % (obj.GetName())

        # residue_colors_group = CreateUserDataGroup(obj, "Residue Colors", c4d.DescID(0))
        #TODO Add color by residues


    return obj


# Main function
def main():
    # Prompt user for needed operations
    do_all, options = getOperations()
    # print do_all, options
    if not do_all and not options:
        return False
    # Can only to partial operations on an existent point cloud
    if not do_all and 'PC' not in options:
        obj = op
        if not obj:
            gui.MessageDialog('Select existing point cloud object and rerun.')
            return False

    # Get the information locally or from server
    fetch = gui.QuestionDialog('Fetch from server? Choose No to load a local file.')
    if fetch:
        # Make sure we have a directory to save downloaded cif
        path = checkPath()
        if not path:
            return False
        os.chdir(path)
        # Get input for structure
        protein = c4d.gui.InputDialog('PDB entry', '')
        if protein == '':
            return False
        # Set cif as format since this is the new default
        ext = '.cif'
        protein_file = protein + ext
        protein_path = './cif/' + protein_file
        pdbl = PDBList()
        pdbl.retrieve_pdb_file(protein, pdir ='./cif', file_format ='mmCif')
    else:
        # For local files
        fn = storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING)
        if fn is None:
            return False
        protein_path = fn
        protein_file = os.path.split(fn)[1]
        protein, ext = os.path.splitext(protein_file)
        # check if pdb is a nucleic acid from http://w3dna.rutgers.edu/index.php/rebuild
        with open(fn) as f:
            first_line = f.readline()
            if 'DNA' in first_line:
                print "PDB is a nucleic acid."
                print first_line
                global nucleic_acid
                nucleic_acid = True

    # Protein in possession. Now let's choose a parser.
    print 'Protein file location: ' + protein_path
    if ext == '.cif':
        parser = FastMMCIFParser()
        print 'Using FastMMCIParser'
    elif ext == '.pdb':
        parser = PDBParser()
        print 'Using PDBParser'
    else:
        gui.MessageDialog('Please select a .cif or .pdb')
        return False

    # Build the primary data
    structure = parser.get_structure(protein, protein_path)


    # Check if multiple models or chains in structure
    multi_model, multi_chain = multiObjects(structure)
    operations = do_all, options

    # Do actual operations
    global simple_struct
    simple_struct = False
    if ext == '.pdb':
        header = parser.get_header()
    else:
        header = False
    # pprint.pprint(header, width=1)
    if not multi_model and not multi_chain:
        print '"%s" is single chain only.' % protein
        chain_name = protein
        atoms = [a for a in structure.get_atoms()]
        if header != False and header['head'] == '':
            print 'No header.'
            simple_struct = True
            chain = structure[0]
        else:
            chain = structure[0]['A']
            if header: pprint(header, width=1)
        obj = doOperations(operations, chain_name, chain, atoms)
    elif multi_model and not multi_chain:
        print '"%s" has multiple models each with a single chain.' % protein
        if header: pprint(header, width=1)
        for model in structure:
            chain = structure[model]['A']  # This will probably break once the case is encountered
            chain_name = protein + '_' + model.get_id()
            atoms = [a for a in model.get_atoms()]
            obj = doOperations(operations, chain_name, chain, atoms)
    elif not multi_model and multi_chain:
        print '"%s" has multiple chains.' % protein
        if header: pprint(header, width=1)
        for model in structure:
            for chain in model:
                chain_name = protein + '_' + chain.get_id()
                atoms = [a for a in chain.get_atoms()]
                obj = doOperations(operations, chain_name, chain, atoms)
    elif multi_model and multi_chain:
        print '"%s" has multiple models and multiple chains.' % protein
        if header: pprint(header, width=1)
        for model in structure:
            for chain in model:
                chain_name = protein + '_' + model.get_id() + '_' + chain.get_id()
                atoms = [a for a in chain.get_atoms()]
                obj = doOperations(operations, chain_name, chain, atoms)

    else:
        print "Error in structure."
        return False



# Execute main()
if __name__=='__main__':
    main()