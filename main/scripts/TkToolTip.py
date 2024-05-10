
"""
########################################
#                                      #
#           Tkinter ToolTips           #
#                                      #
#   Version : v1.01                    #
#   Author  : github.com/Nenotriple    #
#                                      #
########################################

Description:
-------------
This library provides a simple way to add tooltips to any tkinter widget.
It allows customization of the tooltip's delay, position, and text.
"""


import time
from tkinter import Toplevel, Label


class TkToolTip:
    """
    Create a tooltip for any tkinter widget.

    Attributes
    ----------
    widget : widget
        The tkinter widget to which the tooltip is attached.

    text : str
        The text displayed when the tooltip is shown.

    delay : int
        The delay (in ms) before the tooltip is shown.

    x_offset : int
        The x-coordinate offset of the tooltip from the pointer.

    y_offset : int
        The y-coordinate offset of the tooltip from the pointer.

    tip_window : Toplevel
        The Toplevel window used to display the tooltip.

    widget_id : int
        The id returned by the widget's `after` method.

    hide_id : int
        The id returned by the widget's `after` method for hiding the tooltip.

    hide_time : float
        The time when the tooltip was hidden.

    Methods
    -------
    show_tip(x, y):
        Shows the tooltip at the specified screen coordinates.

    hide_tip():
        Hides the tooltip.

    create(widget, text="", delay=0, x_offset=0, y_offset=0):
        Creates a tooltip for the specified widget.

    config(text=None, delay=None, x_offset=None, y_offset=None):
        Configures the tooltip's text, delay, and position offsets.
    """

    def __init__(self, widget, text="", delay=0, x_offset=0, y_offset=0):
        """
        Constructs all the necessary attributes for the TkToolTip object.

        Parameters
        ----------
            widget : widget
                The tkinter widget to which the tooltip is attached.

            text : str, optional
                The text displayed when the tooltip is shown (default is "").

            delay : int, optional
                The delay (in ms) before the tooltip is shown (default is 0).

            x_offset : int, optional
                The x-coordinate offset of the tooltip from the pointer (default is 0).

            y_offset : int, optional
                The y-coordinate offset of the tooltip from the pointer (default is 0).
        """

        self.widget = widget
        self.text = text
        self.delay = delay
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_attributes("-topmost", True)
        self.tip_window.wm_attributes("-disabled", True)
        self.label = Label(self.tip_window, background="#ffffee", relief="ridge", borderwidth=1, justify="left", padx=4, pady=4)
        self.label.pack()
        self.tip_window.withdraw()
        self.widget_id = None
        self.hide_id = None
        self.hide_time = 0


    def show_tip(self, x, y):
        """
        Shows the tooltip at the specified screen coordinates.

        If the tooltip is already shown or if the text is empty, this method does nothing.

        Parameters
        ----------
            x : int
                The x-coordinate of the pointer.

            y : int
                The y-coordinate of the pointer.
        """

        if not self.text or self.tip_window.winfo_viewable():
            return
        x += self.x_offset
        y += self.y_offset
        self.tip_window.wm_geometry(f"+{x}+{y}")
        self.label.config(text=self.text)
        self.tip_window.deiconify()
        self.hide_id = self.widget.after(10000, self.hide_tip)


    def hide_tip(self):
        """
        Hides the tooltip.

        If the tooltip is not shown, this method does nothing.
        """

        if self.tip_window.winfo_viewable():
            self.tip_window.withdraw()
        self.hide_time = time.time()


    @staticmethod
    def create(widget, text="", delay=0, x_offset=0, y_offset=0):
        """
        Creates a tooltip for the specified widget.

        Parameters
        ----------
            widget : widget
                The tkinter widget to which the tooltip is attached.

            text : str, optional
                The text displayed when the tooltip is shown (default is "").

            delay : int, optional
                The delay (in ms) before the tooltip is shown (default is 0).

            x_offset : int, optional
                The x-coordinate offset of the tooltip from the pointer (default is 0).

            y_offset : int, optional
                The y-coordinate offset of the tooltip from the pointer (default is 0).

        Returns
        -------
            TkToolTip
                The created TkToolTip object.
        """

        tool_tip = TkToolTip(widget, text, delay, x_offset, y_offset)
        def enter(event):
            if tool_tip.widget_id:
                widget.after_cancel(tool_tip.widget_id)
            if time.time() - tool_tip.hide_time > 0.1:
                tool_tip.widget_id = widget.after(tool_tip.delay, lambda: tool_tip.show_tip(widget.winfo_pointerx(), widget.winfo_pointery()))
        def leave(event):
            if tool_tip.widget_id:
                widget.after_cancel(tool_tip.widget_id)
            tool_tip.hide_tip()
        def motion(event):
            if tool_tip.widget_id:
                widget.after_cancel(tool_tip.widget_id)
            tool_tip.widget_id = widget.after(tool_tip.delay, lambda: tool_tip.show_tip(widget.winfo_pointerx(), widget.winfo_pointery()))
        widget.bind('<Enter>', enter, add="+")
        widget.bind('<Leave>', leave, add="+")
        widget.bind('<Motion>', motion, add="+")
        widget.bind('<B1-Motion>', leave, add="+")
        return tool_tip


    def config(self, text=None, delay=None, x_offset=None, y_offset=None):
        """
        Configures the tooltip's text, delay, and position offsets.

        Parameters
        ----------
            text : str, optional
                The new text displayed when the tooltip is shown (default is None).

            delay : int, optional
                The new delay (in ms) before the tooltip is shown (default is None).

            x_offset : int, optional
                The new x-coordinate offset of the tooltip from the pointer (default is None).

            y_offset : int, optional
                The new y-coordinate offset of the tooltip from the pointer (default is None).
        """

        if text is not None:
            self.text = text
        if delay is not None:
            self.delay = delay
        if x_offset is not None:
            self.x_offset = x_offset
        if y_offset is not None:
            self.y_offset = y_offset
