"""
########################################
#           Tkinter ToolTips           #
#   Version : v1.06                    #
#   Author  : github.com/Nenotriple    #
########################################

Description:
------------
Add customizable tooltips to any tkinter widget.

Usage:
------
A) Directly create a tooltip:
     TkToolTip.create(widget, text="example")

B) Create and store a tooltip for later configuration:
   tooltip = TkToolTip.create(widget, text="example")
   tooltip.config(text="Example!")

"""


import time
from tkinter import Toplevel, Label

'''Default tooltip parameters'''
TEXT = ""
DELAY = 0
PADX = 0
PADY = 0
IPADX = 2
IPADY = 2
STATE = "normal"
BG = "#ffffe0"
FG = "black"
FONT = ("TkDefaultFont", "8", "normal")
BORDERWIDTH = 1
RELIEF = "solid"
JUSTIFY = "center"
WRAPLENGTH = 0
FADE_IN = 125
FADE_OUT = 50
ORIGIN = "mouse"


class TkToolTip:
    """
    Attach a Tooltip to any tkinter widget.

    Parameters
    ----------
    widget : tkinter.Widget
        The widget to attach the tooltip to

    text : str, optional
        Tooltip text (default is an empty string)

    delay : int, optional
        Delay before showing the tooltip in milliseconds (default is 0)

    padx : int, optional
        X-offset of the tooltip from the origin (default is 0)

    pady : int, optional
        Y-offset of the tooltip from the origin (default is 0)

    ipadx : int, optional
        Horizontal internal padding (default is 0)

    ipady : int, optional
        Vertical internal padding (default is 0)

    state : str, optional
        Tooltip state, "normal" or "disabled" (default is None)

    bg : str, optional
        Background color (default is "#ffffe0")

    fg : str, optional
        Foreground (text) color (default is "black")

    font : tuple, optional
        Font of the text (default is ("TkDefaultFont", 8, "normal"))

    borderwidth : int, optional
        Border width (default is 1)

    relief : str, optional
        Border style (default is "solid")

    justify : str, optional
        Text justification (default is "center")

    wraplength : int, optional
        Maximum line width for text wrapping (default is 0, which disables wrapping)

    fade_in : int, optional
        Fade-in time in milliseconds (default is 125)

    fade_out : int, optional
        Fade-out time in milliseconds (default is 50)

    origin : str, optional
        Origin point of the tooltip, "mouse" or "widget" (default is "mouse")


    Methods
    -------
    create(cls, widget, **kwargs)
        Create a tooltip for the widget with the given parameters.

    config(**kwargs)
        Update the tooltip configuration.
    """


    def __init__(self,
                 widget,
                 text=TEXT,
                 delay=DELAY,
                 padx=PADX,
                 pady=PADY,
                 ipadx=IPADX,
                 ipady=IPADY,
                 state=STATE,
                 bg=BG,
                 fg=FG,
                 font=FONT,
                 borderwidth=BORDERWIDTH,
                 relief=RELIEF,
                 justify=JUSTIFY,
                 wraplength=WRAPLENGTH,
                 fade_in=FADE_IN,
                 fade_out=FADE_OUT,
                 origin=ORIGIN
                 ):

        self.widget = widget
        self.text = text
        self.delay = delay
        self.padx = padx
        self.pady = pady
        self.ipadx = ipadx
        self.ipady = ipady
        self.state = state
        self.bg = bg
        self.fg = fg
        self.font = font
        self.borderwidth = borderwidth
        self.relief = relief
        self.justify = justify
        self.wraplength = wraplength
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.origin = origin

        self.tip_window = None
        self.widget_id = None
        self.hide_id = None
        self.hide_time = None

        self._bind_widget()


    def _bind_widget(self):
        """Setup event bindings for the widget."""
        self.widget.bind('<Motion>', self._schedule_show_tip, add="+")
        self.widget.bind('<Enter>', self._schedule_show_tip, add="+")
        self.widget.bind('<Leave>', self._leave_event, add="+")
        self.widget.bind("<Button-1>", self._leave_event, add="+")
        self.widget.bind('<B1-Motion>', self._leave_event, add="+")


    def _leave_event(self, event):
        """Hide the tooltip and cancel any scheduled events."""
        self._cancel_tip()
        self._hide_tip()


    def _schedule_show_tip(self, event):
        """Schedule the tooltip to be shown after the specified delay."""
        if self.widget_id:
            self.widget.after_cancel(self.widget_id)
        self.widget_id = self.widget.after(self.delay, lambda: self._show_tip(event))


    def _show_tip(self, event):
        """Display the tooltip at the specified position."""
        if self.state == "disabled" or not self.text:
            return
        x, y = (event.x_root + self.padx, event.y_root + self.pady) if self.origin == "mouse" else \
               (self.widget.winfo_rootx() + self.padx, self.widget.winfo_rooty() + self.pady)
        self._create_tip_window(x, y)


    def _create_tip_window(self, x, y):
        """Create and display the tooltip window."""
        if self.tip_window:
            return
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        self.tip_window.attributes("-alpha", 0.0 if self.fade_in else 1.0)
        label = Label(self.tip_window,
                      text=self.text,
                      background=self.bg,
                      foreground=self.fg,
                      font=self.font,
                      relief=self.relief,
                      borderwidth=self.borderwidth,
                      justify=self.justify,
                      wraplength=self.wraplength
                      )
        label.pack(ipadx=self.ipadx,
                   ipady=self.ipady
                   )
        if self.fade_in:
            self._fade(self.fade_in, 0.0, 1.0)


    def _hide_tip(self):
        """Hide or fade out the tooltip window."""
        if self.tip_window:
            if self.fade_out:
                self._fade(self.fade_out, 1.0, 0.0, on_complete=self._remove_tip_window)
            else:
                self._remove_tip_window()


    def _cancel_tip(self):
        """Cancel the scheduled display of the tooltip."""
        if self.widget_id:
            self.widget.after_cancel(self.widget_id)
            self.widget_id = None


    def _remove_tip_window(self):
        """Withdraw and remove the tooltip window."""
        if self.tip_window:
            self.tip_window.withdraw()
            self.tip_window = None
            self.hide_time = time.time()


    def _fade(self, duration, start_alpha, end_alpha, on_complete=None):
        """Fade the tooltip window in or out."""
        if self.tip_window is None:
            return
        steps = max(1, duration // 10)
        alpha_step = (end_alpha - start_alpha) / steps

        def step(current_step):
            if self.tip_window is None:
                return
            alpha = start_alpha + current_step * alpha_step
            self.tip_window.attributes("-alpha", alpha)
            if current_step < steps:
                self.tip_window.after(10, step, current_step + 1)
            else:
                if on_complete:
                    on_complete()
        step(0)


    def config(self,
               text=None,
               delay=None,
               padx=None,
               pady=None,
               ipadx=None,
               ipady=None,
               state=None,
               bg=None,
               fg=None,
               font=None,
               borderwidth=None,
               relief=None,
               justify=None,
               wraplength=None,
               fade_in=None,
               fade_out=None,
               origin=None
               ):
        """Update the tooltip configuration with the given parameters."""
        for param, value in locals().items():
            if value is not None:
                if param == 'state':
                    assert value in ["normal", "disabled"], "Invalid state"
                setattr(self, param, value)


    @classmethod
    def create(cls,
               widget,
               text=TEXT,
               delay=DELAY,
               padx=PADX,
               pady=PADY,
               ipadx=IPADX,
               ipady=IPADY,
               state=STATE,
               bg=BG,
               fg=FG,
               font=FONT,
               borderwidth=BORDERWIDTH,
               relief=RELIEF,
               justify=JUSTIFY,
               wraplength=WRAPLENGTH,
               fade_in=FADE_IN,
               fade_out=FADE_OUT,
               origin=ORIGIN
               ):
        """Create a tooltip for the specified widget with the given parameters."""
        return cls(widget, text, delay, padx, pady, ipadx, ipady, state, bg, fg, font, borderwidth, relief, justify, wraplength, fade_in, fade_out, origin)


#endregion
################################################################################################################################################
#region -  Changelog


'''


v1.06 changes:


  - New:
    - Added `justify` parameter: Configure text justification in the tooltip. (Default is "center")
    - Added `wraplength` parameter: Configure the maximum line width for text wrapping. (Default is 0, which disables wrapping)
    - Added `fade_in` and `fade_out` parameters: Configure fade-in and fade-out times. (Default is 100 and 50, ms)
    - Added `origin` parameter: Configure the origin point of the tooltip. (Default is "mouse")


<br>


  - Fixed:
    - Issue where the underlying widget would be impossible to interact with after hiding the tooltip.


<br>


  - Other changes:
    - Now uses `TkDefaultFont` instead of Tahoma as the default font for the tooltip text.
    - Refactored the code to be more readable and maintainable.


'''


#endregion

'''


- Todo
  - Rounded corners for the tooltip, and a more modern look theme.
  - In addition to the 'origin' parameter, it would be handy to set the 'anchor' for the origin.
    - The anchor would dictate the starting (x,y) position inside the origin.
    - For example, the anchor could be considered to already by "ne" (north east), or "top left" for the current logic.
    - Changing the anchor to "se" would set the tooltip to appear in the bottom right when 'origin=widget'.
  - When (origin="mouse") allow for a 'follow' parameter to make the tooltip follow the mouse.
  - Add a 'hide_delay' parameter to keep the tooltip visible for a set amount of time after the mouse leaves the widget.
  - Stop the tooltip from being created outside the screen bounds.
  - Add a 'shadow' parameter that adds a soft drop shadow under the tooltip.


- Tofix
  -

  '''