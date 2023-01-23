import wx

class SetupDialog(wx.Frame):
    # TODO:
    """Construct an initialization window asking for the IP addresses of
    the raspberry pies as well as the desired geometry. The user must
    be able to select also if they want automatic or manual exposure, as
    well as the destination directory of the images. Optionally, certain
    images can also be selected to be vertically flipped, to correct
    for a possible misalignment.

    There must also be a possibility of selecting a previous config file.
    """

    def __init__(self, parent):
        super().__init__(self, parent)

    def OnCheckConfig(self, event):
        pass

    def OnAccept(self, event):
        pass

    def OnLoadCfg(self, event):
        pass
