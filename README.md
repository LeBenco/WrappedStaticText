A `wx.StaticText` with advanced wrapping management. Every possible wrapping of the label is computed (can be CPU-consuming if label has many spaces) and the best one is selected, i.e. the one that respects the wrapping rule and uses the smallest number of rows. If no wrapping is possible, an ellipsed label is used, based on the least wide and high combination.

Please note that this is a proof of concept and may require adaptation to meet specific needs.

Example:
```python
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
```
