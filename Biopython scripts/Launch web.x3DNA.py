# Copyright (c) 2017  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import c4d

defpage = "http://web.x3dna.org/index.php/fibermodel"

class Dialog(c4d.gui.GeDialog):
    
    def __init__(self):
        c4d.gui.GeDialog.__init__(self)
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
    
    def CreateLayout(self):
        self.SetTitle("Web Browser")
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 0, 1)
        self.GroupBorderSpace(2, 2, 2, 0)
        self.AddGadget(c4d.DIALOG_PIN, 0)
        self.AddEditText(1001, c4d.BFH_SCALEFIT)
        self.GroupEnd()
        self.b = self.AddCustomGui(1000, c4d.CUSTOMGUI_HTMLVIEWER, "",
            c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 200, 200)
        return True

    def InitValues(self):
        self.SetString(1001, defpage)
        self.Command(1, None)
        return True

    def Command(self, wid, bc):
        if wid == c4d.DLG_OK:  # Enter pressed
            url = self.GetString(1001)
            self.b.SetUrl(url, c4d.URL_ENCODING_UTF16)
        return True

dlg = Dialog()
dlg.Open(c4d.DLG_TYPE_ASYNC)