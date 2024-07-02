import wx
import sys

################################################################################
############################## Wrapped Static Text #############################

class WrappedStaticText(wx.StaticText):
    """
    A StaticText with advanced wrapping management. Every possible wrapping
    of the label is computed (can be CPU-consuming if label has many spaces)
    and the best one is selected, i.e. the one that respects the wrapping rule
    and uses the smallest number of rows. If no wrapping is possible, an
    ellipsed label is used, based on the least wide and high combination.
    """
    def __init__(self, parent, label, width, font, max_rows=None, center=False):
        """
        Constructor.
        
        * `parent`: wx parent,
        * `label`: text to be displayed wrapped
        * `width`: width on which `label` is wrapped
        * `font`: Font used to compute xrapping and display the wrapped label
        * `center`: Whether the wrapped label is centered
        """
        super().__init__(parent)
        
        self.center = center
        self.unwrappedLabel = label
        self.wrappedWidth = width
        self.maxRows = max_rows
        
        self.SetFont(font)
        self.SetLabel(label)
        self.Bind(wx.EVT_PAINT, self._OnPaint) 

    def SetLabel(self, label):
        """
        Changes the text's label. Recompute the wrapped label
        
        * `label`: new label to wrap and display
        """
        dc = wx.ScreenDC()
        dc.SetFont(self.GetFont())
        
        label_split = label.split()
        
        ## For wrapping label
        best_height = sys.maxsize
        best_height = sys.maxsize
        best_label = None
        
        ## For ellipsis if wrapping is not possible because of too long word
        best_unwrapped_height = sys.maxsize
        best_unwrapped_width = sys.maxsize
        best_unwrapped_label = None
        labels = self._GetWrappings(label_split[0], label_split[1:])
        
        ## Search for the best label
        for l in labels:
            w,h = dc.GetMultiLineTextExtent(l)
            
            ## Update best wrapping
            if w <= self.wrappedWidth:
                if h < best_height:
                    best_label  = l
                    best_height = h
            ## Update best ellipsis in case of wrapping fail
            elif h == best_unwrapped_height:
                 if w < best_unwrapped_width:
                        best_unwrapped_label  = l
                        best_unwrapped_width = w
            elif h < best_unwrapped_height:
                        best_unwrapped_label  = l
                        best_unwrapped_widtht = w
                        best_unwrapped_height = h
        
        ## In case of wrapping fail, search for the best ellipsed label
        if best_label == None:
            while best_unwrapped_width > self.wrappedWidth:
                best_unwrapped_label = best_unwrapped_label[:-1]
                best_unwrapped_width = \
                    dc.GetMultiLineTextExtent(best_unwrapped_label+"…")[0]
            best_label = best_unwrapped_label+"…"
        super().SetLabel(best_label)

    def SetFont(self, font):
        """
        Changes the text's font. Recompute the wrapped label
        
        * `font`: new font to wrap and display the text's label with
        """
        super().SetFont(font)
        self.SetLabel(self.unwrappedLabel)

    def _GetWrappings(self, text, words):
        """
        Recursively compute all combinations of text splitting using either a
        space or a new line. May be time-consuming if label has too many spaces.
        
        * `text`: beginning of the full label, already wrapped
        * `words`: list of remaining words to be added to `text`
        
        * yields: every combinations of `text` and remaining words, concatenated
          either with `'\n'` ot `' '`
        """
        if len(words) == 0:
            # if there is no space at all in the unwrapped label
            yield text
        elif len(words) == 1:
            ## if it's the last word of the text, just yield the two versions
            yield text+" "  + words[0]
            yield text+"\n" + words[0]
        else:
            ## try the two spliting combinations, and recursively compute the
            #  wrapping for the remaining text
            yield from self._GetWrappings(text+" "  + words[0], words[1:])
            yield from self._GetWrappings(text+"\n" + words[0], words[1:])
    
    def _OnPaint(self, event):
        """
        Paint callback. Overrides the paint event callback so that centered text
        painting renders the right way with wrapped text.
        """
        dc = wx.PaintDC(self) 
        dc.Clear()

        curr_width, curr_height = self.GetSize()
        
        label_h = 0
        for line in self.GetLabel().split("\n"):
            text_w, text_h = dc.GetTextExtent(line)
            if self.center:
                w = (curr_width - text_w)/2
            else:
                w = 0
            dc.DrawText(line, int(w), int(label_h))
            label_h+=text_h


if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(parent=None, title='Exemple WrappedStaticText')
    panel = wx.Panel(frame)

    font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    wrapped_text = WrappedStaticText(panel, "This is a very long text that must"
                                            "be displayed wrapped in a limited space.",
                                     200, font, max_rows=3, center=True)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wrapped_text, 1, wx.EXPAND | wx.ALL, 10)
    panel.SetSizer(sizer)

    frame.Show()
    app.MainLoop()