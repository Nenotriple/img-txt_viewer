"""ScrollableFrame module.

A Canvas with an inner Frame and optional scrollbars.

Minimal usage:
    from scrollable_frame import ScrollableFrame
    root = tk.Tk()
    sf = ScrollableFrame(root, layout="vertical")
    sf.pack(fill="both", expand=True)
    tk.Button(sf.frame, text="A Button").pack()
"""

#region Imports


import tkinter as tk
from tkinter import ttk


#endregion
#region _BaseScrollableFrame


class _BaseScrollableFrame:
    """Base scroll logic: Canvas + embedded Frame, scrollbars, and mousewheel handling.

        Parameters
        ----------
        layout : str
            One of 'vertical', 'horizontal', or 'both' indicating which scrollbars
            to create/bind. This name matches the internal attribute
            ``self.layout`` and the validator method.
    """
    def __init__(self, master, layout="vertical", *args, **kwargs):
        self.layout = self._validate_layout(layout)
        self._setup_scroll_canvas(master)
        self._bind_mousewheel_events()


    def _validate_layout(self, layout):
        """Ensure layout is 'vertical', 'horizontal', or 'both'."""
        if layout not in ("vertical", "horizontal", "both"):
            raise ValueError("layout must be 'vertical', 'horizontal', or 'both'")
        return layout


    def _setup_scroll_canvas(self, master):
        """Create Canvas and a Frame window for content, bind config events."""
        self.canvas = tk.Canvas(master, highlightthickness=0)
        self._setup_scrollbars(master)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content_frame = ttk.Frame(self.canvas)
        self.content_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.frame = self.content_frame
        self.content_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)


    def _setup_scrollbars(self, master):
        """Create vertical and/or horizontal ttk.Scrollbar widgets as requested."""
        if self.layout in ("vertical", "both"):
            self.vsb = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vsb.set)
            self.vsb.pack(side="right", fill="y")
        if self.layout in ("horizontal", "both"):
            self.hsb = ttk.Scrollbar(master, orient="horizontal", command=self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.hsb.set)
            self.hsb.pack(side="bottom", fill="x")


    def _bind_mousewheel_events(self):
        """Bind enter/leave handlers; actual wheel sequences are bound dynamically."""
        # Only bind enter/leave handlers here. Actual mousewheel sequences
        # are bound/unbound dynamically in _on_enter/_on_leave based on
        # whether the content is scrollable on each axis.
        self.canvas.bind("<Enter>", self._on_enter, add="+")
        self.canvas.bind("<Leave>", self._on_leave, add="+")
        self.content_frame.bind("<Enter>", self._on_enter, add="+")
        self.content_frame.bind("<Leave>", self._on_leave, add="+")


#endregion
#region Events


    def _on_frame_configure(self, _event):
        """Update canvas scrollregion and scrollable state."""
        # Always update scrollregion to the full bounding box of the content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # update cached scrollable state after content changes
        self._update_scrollable_state()


    def _on_canvas_configure(self, event):
        """Adjust embedded window size for single-axis layouts and update state."""
        # Only set width/height if the corresponding scrollbar is NOT present
        # This allows the content to expand beyond the visible area and be scrollable
        if self.layout == "vertical":
            self.canvas.itemconfig(self.content_window, width=event.width)
        elif self.layout == "horizontal":
            self.canvas.itemconfig(self.content_window, height=event.height)
        # For "both", do not force width or height, let content grow freely
        # update cached scrollable state after canvas size changes
        self._update_scrollable_state()



    def _on_enter(self, _event):
        """Recompute scrollable state and bind wheel sequences for available axes."""
        # Recompute scrollable state to make an informed decision.
        try:
            self._update_scrollable_state()
        except Exception:
            # safe fallback: assume not scrollable
            pass
        # Bind vertical wheel if vertical scrolling is available and a vertical scrollbar/layout supports it
        if self._scrollable_state.get("vertical", False) and self.layout in ("vertical", "both"):
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        else:
            # ensure any previously bound vertical sequence is removed
            try:
                self.canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
        # Bind horizontal (shift-wheel) if horizontal scrolling is available and layout supports it
        if self._scrollable_state.get("horizontal", False) and self.layout in ("horizontal", "both"):
            # Using Shift-MouseWheel as a separate sequence allows per-axis bind/unbind
            self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel, add="+")
        else:
            try:
                self.canvas.unbind_all("<Shift-MouseWheel>")
            except Exception:
                pass


    def _on_leave(self, _event):
        """Unbind wheel sequences when pointer leaves."""
        # Unbind both sequences when leaving to avoid capturing wheel events when not over widget
        for seq in ("<MouseWheel>", "<Shift-MouseWheel>"):
            try:
                self.canvas.unbind_all(seq)
            except Exception:
                pass


    def _on_mousewheel(self, event):
        """Map mousewheel to xview/yview; returns 'break' when handled."""
        if not self._event_targets_self(event.widget):
            return
        units = self._get_scroll_units(event)
        # Keep original shift-detection for compatibility; Shift-MouseWheel may also set state.
        is_shift = bool(getattr(event, "state", 0) & 0x1)
        if is_shift:
            if self.layout in ("horizontal", "both") and self._scrollable_state.get("horizontal", False):
                self.canvas.xview_scroll(units, "units")
                return "break"
        else:
            if self.layout in ("vertical", "both") and self._scrollable_state.get("vertical", False):
                self.canvas.yview_scroll(units, "units")
                return "break"


    def _event_targets_self(self, widget):
        """Return True if widget is the canvas or a descendant."""
        while widget:
            if widget == self.canvas:
                return True
            widget = getattr(widget, "master", None)
        return False


#endregion
#region Helpers


    @staticmethod
    def _get_scroll_units(event):
        """Turn event.delta into integer scroll units."""
        delta = getattr(event, "delta", 0)
        if delta:
            if abs(delta) >= 120:
                magnitude = abs(delta) // 120
            else:
                magnitude = 1
            return -int(delta / abs(delta)) * magnitude
        return 0


    def _update_scrollable_state(self):
        """Recompute cached scrollable state and emit <<ScrollStateChanged>> if changed."""
        prev = getattr(self, "_scrollable_state", None)
        v = self._is_axis_scrollable("vertical")
        h = self._is_axis_scrollable("horizontal")
        self._scrollable_state = {"vertical": v, "horizontal": h}
        if prev is None or prev != self._scrollable_state:
            try:
                self.canvas.event_generate("<<ScrollStateChanged>>", when="tail")
            except Exception:
                pass


    def _is_axis_scrollable(self, axis):
        """Return True if the content is larger than the canvas view on the axis."""
        try:
            if axis == "vertical":
                first, last = self.canvas.yview()
            elif axis == "horizontal":
                first, last = self.canvas.xview()
            else:
                raise ValueError("axis must be 'vertical' or 'horizontal'")
        except Exception:
            return False
        # If the whole content is visible, view() returns (0.0, 1.0)
        return not (abs(first - 0.0) < 1e-9 and abs(last - 1.0) < 1e-9)


#endregion
#region ScrollableFrame


class ScrollableFrame(ttk.Frame, _BaseScrollableFrame):
    """Drop-in ttk.Frame container with an inner scrollable .frame.

    Use layout='vertical'|'horizontal'|'both'. Pass label to wrap
    content in a ttk.LabelFrame.
    """
    def __init__(self, master, layout="vertical", label=None, *args, **kwargs):
        """Initialize the ScrollableFrame container."""
        # Initialize the outer frame (this instance) which remains the widget to pack/grid.
        ttk.Frame.__init__(self, master, *args, **kwargs)
        if label is not None:
            self._inner_container = ttk.LabelFrame(self, text=label)
            self._inner_container.pack(fill="both", expand=True)
            base_parent = self._inner_container
        else:
            self._inner_container = None
            base_parent = self
        # Initialize the scrollable machinery using the chosen container as the master.
        _BaseScrollableFrame.__init__(self, base_parent, layout, *args, **kwargs)


#endregion
#region Main/Demo


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scrollable Frame Demo")
    root.geometry("400x300")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Vertical scrollbar
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Vertical")
    scrollable_v = ScrollableFrame(tab1, layout="vertical")
    scrollable_v.pack(fill="both", expand=True)
    for i in range(20):
        ttk.Button(scrollable_v.frame, text=f"Button {i+1}").pack(side="top", fill="x", padx=10, pady=2)

    # Horizontal scrollbar
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Horizontal")
    scrollable_h = ScrollableFrame(tab2, layout="horizontal")
    scrollable_h.pack(fill="both", expand=True)
    for i in range(10):
        ttk.Button(scrollable_h.frame, text=f"Wide Button {i+1}" * 5).pack(side="left", padx=10, pady=2)

    # Both scrollbars
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Both")
    scrollable_both = ScrollableFrame(tab3, layout="both")
    scrollable_both.pack(fill="both", expand=True)
    for i in range(15):
        for j in range(5):
            ttk.Button(scrollable_both.frame, text=f"Button ({i+1},{j+1})").grid(row=i, column=j, padx=10, pady=10, sticky="ew")

    # LabelFrame example
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="LabelFrame")
    scrollable_label = ScrollableFrame(tab4, layout="vertical", label="Labeled Scrollable Frame")
    scrollable_label.pack(fill="both", expand=True)
    for i in range(10):
        ttk.Label(scrollable_label.frame, text=f"Label {i+1}").pack(anchor="w", padx=10, pady=2)

    root.mainloop()


#endregion
