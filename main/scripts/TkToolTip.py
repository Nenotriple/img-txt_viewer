"""


########################################
#                                      #
#           Tkinter ToolTips           #
#                                      #
#   Version : v1.06                    #
#   Author  : github.com/Nenotriple    #
#                                      #
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


    def __init__(self, widget, text=TEXT, delay=DELAY, padx=PADX, pady=PADY, ipadx=IPADX, ipady=IPADY,
                 state=STATE, bg=BG, fg=FG, font=FONT, borderwidth=BORDERWIDTH, relief=RELIEF,
                 justify=JUSTIFY, wraplength=WRAPLENGTH, fade_in=FADE_IN, fade_out=FADE_OUT, origin=ORIGIN):
        """
        Initialize the tooltip with the given parameters.
        """
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

        self.tip_window = None  # Window; None if not shown
        self.widget_id = None  # Display event ID; None if not scheduled
        self.hide_id = None  # Hide event ID; None if not scheduled
        self.hide_time = None  # Last hidden timestamp; None if never hidden

        self._bind_widget()


    def _bind_widget(self):
        """Setup event bindings for the widget."""
        self.widget.bind('<Enter>', self._enter, add="+")
        self.widget.bind('<Leave>', self._leave, add="+")
        self.widget.bind('<Motion>', self._motion, add="+")
        self.widget.bind("<Button-1>", self._leave, add="+")
        self.widget.bind('<B1-Motion>', self._leave, add="+")


    def _enter(self, event):
        """Schedule tooltip display after the specified delay."""
        self._schedule_show_tip(event)


    def _leave(self, event):
        """Hide the tooltip and cancel any scheduled events."""
        self._cancel_tip()
        self._hide_tip()


    def _motion(self, event):
        """Reschedule the tooltip display when the cursor moves within the widget."""
        self._schedule_show_tip(event)


    def _schedule_show_tip(self, event):
        """Schedule the tooltip to be shown after the specified delay."""
        if self.widget_id:
            self.widget.after_cancel(self.widget_id)
        self.widget_id = self.widget.after(self.delay, lambda: self._show_tip(event))


    def _show_tip(self, event):
        """Display the tooltip at the specified position."""
        if self.state == "disabled":
            return
        if self.origin == "mouse":
            x = event.x_root + self.padx
            y = event.y_root + self.pady
        else:
            x = self.widget.winfo_rootx() + self.padx
            y = self.widget.winfo_rooty() + self.pady
        self._create_tip_window(x, y)


    def _create_tip_window(self, x, y):
        """Create and display the tooltip window."""
        if self.tip_window or not self.text:
            return
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        if self.fade_in > 0:
            self.tip_window.attributes("-alpha", 0.0)
        label = Label(self.tip_window, text=self.text, background=self.bg, foreground=self.fg,
                      font=self.font, relief=self.relief, borderwidth=self.borderwidth, justify=self.justify,
                      wraplength=self.wraplength)
        label.pack(ipadx=self.ipadx, ipady=self.ipady)
        if self.fade_in > 0:
            self._fade_in()
        else:
            self.tip_window.attributes("-alpha", 1.0)


    def _hide_tip(self):
        """Destroy the tooltip window if it exists."""
        if self.tip_window:
            if self.fade_out > 0:
                self._fade_out()
            else:
                self.tip_window.withdraw()
                self.tip_window = None
                self.hide_time = time.time()


    def _fade_in(self):
        """Gradually fade in the tooltip window."""
        if self.fade_in > 0:
            self._fade_step(0.0, 1.0, self.fade_in, self.tip_window, "in")


    def _fade_out(self):
        """Gradually fade out the tooltip window."""
        if self.fade_out > 0:
            self._fade_step(1.0, 0.0, self.fade_out, self.tip_window, "out")


    def _fade_step(self, start_alpha, end_alpha, duration, window, direction):
        step_duration = max(1, duration // 10)
        alpha_increment = (end_alpha - start_alpha) / step_duration

        def step(current_step):
            alpha = start_alpha + current_step * alpha_increment
            window.attributes("-alpha", alpha)
            if current_step < step_duration:
                window.after(10, step, current_step + 1)
            else:
                if direction == "out":
                    window.withdraw()
                    self.tip_window = None
                    self.hide_time = time.time()
        step(0)


    def _cancel_tip(self):
        """Cancel the scheduled display of the tooltip."""
        if self.widget_id:
            self.widget.after_cancel(self.widget_id)
            self.widget_id = None


    def config(self, text=None, delay=None, padx=None, pady=None, ipadx=None, ipady=None, state=None,
               bg=None, fg=None, font=None, borderwidth=None,
               relief=None, justify=None, wraplength=None, fade_in=None, fade_out=None, origin=None):
        """Update the tooltip configuration with the given parameters."""
        for param, value in locals().items():
            if value is not None:
                if param == 'state':
                    assert value in ["normal", "disabled"], "Invalid state"
                setattr(self, param, value)


    @classmethod
    def create(cls, widget, text=TEXT, delay=DELAY, padx=PADX, pady=PADY, ipadx=IPADX, ipady=IPADY,
                 state=STATE, bg=BG, fg=FG, font=FONT, borderwidth=BORDERWIDTH, relief=RELIEF,
                 justify=JUSTIFY, wraplength=WRAPLENGTH, fade_in=FADE_IN, fade_out=FADE_OUT, origin=ORIGIN):
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


'''


#endregion

'''


- Todo
  - It would be handy to configure where the tooltip "origin" is. Currently it's always the mouse x/y position, but it could be based on the widget's position, or a custom x/y position, etc.
    - Having the ability to configure the "origin" and anchor point would allow for more flexibility in the tooltip's positioning.
    - The anchor point would be the point on a widget where the tooltip is positioned relative to.


- Tofix
  -

  '''