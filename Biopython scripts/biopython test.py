import os
import pprint

from Bio.PDB.MMCIFParser import FastMMCIFParser
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.PDBList import PDBList
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

protein = 'Aggrecan CS'

pdbl = PDBList()
# pfile = pdbl.retrieve_pdb_file(protein, pdir ='./cif', file_format ='mmCif')
pfile = "E:\Dropbox\Sci Viz\BioVisualization\pdb\Aggrecan CS.pdb"

# parser = FastMMCIFParser()
parser = PDBParser()

mmcif_dict = MMCIF2Dict(pfile)

structure = parser.get_structure(protein, pfile)

chain = structure[0]