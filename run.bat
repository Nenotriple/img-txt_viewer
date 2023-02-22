@echo OFF
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
python img-txt_viewer.py
exit

::This bat file is only used as a way of hiding the CMD prompt that opens with the img-txt_viewer ui window.
