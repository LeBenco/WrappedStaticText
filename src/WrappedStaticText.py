"""
MIT License

Copyright (c) 2024 Benjamin Cohen Boulakia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
    def __init__(self, parent, line_spacing_factor=0,
                 non_breaking_spaces = True, justify_last_line = False,
                 max_space_width_factor= 1.6, *args, **kwargs):
              """
        Constructor.

        Parameters:
        * `parent`: wx parent widget.
        * `line_spacing_factor` (float): Factor applied to the current font size
            to compute line spacing. Default is 0.
        * `non_breaking_spaces` (bool): If True, common rules for non-breaking
            spaces are applied (e.g., forbid wrap after «). Default is True.
        * `justify_last_line` (bool): If True, the last line of text will be justified.
            Default is False.
        * `max_space_width_factor` (float): Maximum width factor for spaces when justifying.
            Default is 1.6.
        * `*args`: Additional positional arguments passed to wx.StaticText constructor.
        * `**kwargs`: Additional keyword arguments passed to wx.StaticText constructor.

        Note:
        The `style` parameter (either in args or kwargs) will always have
        `wx.ST_NO_AUTORESIZE` added to it. If `style` is not provided, it will
        be set to `wx.ST_NO_AUTORESIZE`.
        """
                     
        self._nonBreakingSpaces = non_breaking_spaces
        
        # First thing todo is to extract `style` from arguments in order to add
        # wx.ST_NO_AUTORESIZE to it
        
        # Find the position of 'style' in the parent's __init__ method
        parent_params = wx.StaticText.__init__.__code__.co_varnames
        style_index = parent_params.index('style') if 'style' in parent_params else -1

        # Update style in args or kwargs with wx.ST_NO_AUTORESIZE
        if "style" in wx.StaticText.__init__.__code__.co_varnames:
            args_list = list(args)
            style_index = wx.StaticText.__init__.__code__.co_varnames.index("style")
            args_list[style_index] = args_list[style_index] | wx.ST_NO_AUTORESIZE
            args = tuple(args_list)
        else:
            kwargs["style"] = kwargs.get("style", 0) | wx.ST_NO_AUTORESIZE

        # Call parent constructor
        super().__init__(parent, *args, **kwargs)
        self.line_spacing_factor = line_spacing_factor
        self.justify_last_line = justify_last_line
        self.max_space_width_factor = max_space_width_factor
        self.Bind(wx.EVT_PAINT, self._OnPaint)

    def SetLabel(self, label):
        """
        Changes the text's label. Recompute the wrapped label
        
        * `label`: new label to wrap and display
        """
        self._unwrappedLabel = label
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
        self.SetLabel(self._unwrappedLabel)

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
    
    def _OnResize(self, event):
        """
        Paint callback. Overrides the paint event callback so that centered text
        painting renders the right way with wrapped text.
        """
        self.SetLabel(self._unwrappedLabel)
