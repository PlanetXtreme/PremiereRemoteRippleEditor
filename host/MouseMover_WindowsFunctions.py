import os
import shutil
import time
import psutil
import pyautogui
import time
from datetime import datetime
from pynput import keyboard
from pynput.keyboard import GlobalHotKeys, Controller, Key, Listener
import pynput
import threading
import queue
import sys
import ctypes
from ctypes import wintypes
from screeninfo import get_monitors
from ahk import AHK
import re
import screeninfo
from fractions import Fraction
import pyperclip


# NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES    NOTES

# DO NOT SET KEYBINDS FOR "+", "=", "\", "\\". These are required for other functions. 
# Ensure that when recording coordinates, you account for "windowed" or "not windowed" mode, configured by the variable "is_windowed".
# LAUNCH AS ADMINISTRATOR. LAUNCH AS ADMIN. This is because if you don't, some of the keybind actions WILL NOT WORK since you need
# to be an admin to do some complicated mouse-moving and keyboard pressing automation stuff.

# IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES    IGNORE THESE DEFAULT VARIABLES
# IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES    IGNORE THESE DEFAULT VARIABLES
# IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES    IGNORE THESE DEFAULT VARIABLES
# IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES     IGNORE THESE DEFAULT VARIABLES    IGNORE THESE DEFAULT VARIABLES

is_windowed = True #IF YOU USE WINDOWED MODE, SET AS True. If borderless or fullscreen, set to False. May not matter for certain games.
is_windowed_px = 40
keyboard_controller = Controller()
ahk = AHK()
pyautogui.PAUSE = 0.001
ENUM_CURRENT_SETTINGS = -1      # no idea but it's supposedly needed

# COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING
# COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING    COORDINATE HANDLING

# "Stretch functions" (the below 3) stretch input coordinates to fill the entire selected monitor irregardless of aspect ratio.
# This squashes/stretches coordinates, unlike the letterboxing functions which preserve the original 16:9 proportions.
# Test if this or the letterboxing function is preferred by rotating a secondary monitor, and testing the positioning
# of the mouse relative to the changed aspect ratios.
#FindMousePos_Stretch   FindMousePos_Stretch   FindMousePos_Stretch   FindMousePos_Stretch   FindMousePos_Stretch   
def stretchCoordsHELPER(x, y, monitor):
    """
    Reverse scale coordinates from 3840x2160 theoretical space back to the actual monitor dimensions.
    Adjusts for windowed mode by adding 40px to monitor height if necessary.
    """
    global is_windowed

    monitor_width = monitor.width
    monitor_height = monitor.height - is_windowed_px if is_windowed else monitor.height

    # Reverse scale from 3840x2160 theoretical space
    actual_x = (x / 3840) * monitor_width
    actual_y = (y / 2160) * monitor_height

    return round(actual_x), round(actual_y)

def clickFuncStretch(coordinates, selected_monitor=None, printStatements=True):
    global is_windowed

    # Auto-detect monitor if not provided
    if selected_monitor is None:
        if printStatements:
            print("DEBUG: No monitor selected. Detecting monitor under mouse...")

        # Use helper
        details = get_monitor_details_under_mouse()

        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine Origin using the handle from details
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

        # Convert dict into a simple object with attributes
        class MonitorObj:
            pass

        selected_monitor = MonitorObj()
        selected_monitor.name = mon_name
        selected_monitor.width = log_w
        selected_monitor.height = log_h
        selected_monitor.x = mon_origin_x
        selected_monitor.y = mon_origin_y
        selected_monitor.phys_w = phys_w
        selected_monitor.phys_h = phys_h
        selected_monitor.relative_scale = target_scale

        if printStatements:
            print(f"Detected monitor: {selected_monitor.name} at ({selected_monitor.x}, {selected_monitor.y})")

    # Unpack coordinates
    x, y = coordinates

    # Reverse scale the coordinates
    adjusted_x, adjusted_y = stretchCoordsHELPER(x, y, selected_monitor)

    # Handle windowed mode adjustment
    if is_windowed:
        adjusted_y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates by adding the monitor's offset
    global_x = adjusted_x + selected_monitor.x
    global_y = adjusted_y + selected_monitor.y

    # Debugging print statements
    if printStatements:
        print(f"Adjusted Coordinates: ({adjusted_x}, {adjusted_y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Click the mouse
    pyautogui.click(global_x, global_y)
    if printStatements:
        print(f"Moved to global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

def moveToFuncStretch(coordinates, duration=0.8, selected_monitor=None, printStatements=True):
    global is_windowed

    # Auto-detect monitor if not provided
    if selected_monitor is None:
        if printStatements:
            print("DEBUG: No monitor selected. Detecting monitor under mouse...")

        # Use helper
        details = get_monitor_details_under_mouse()

        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine Origin using the handle from details
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

        # Convert dict into a simple object with attributes
        class MonitorObj:
            pass

        selected_monitor = MonitorObj()
        selected_monitor.name = mon_name
        selected_monitor.width = log_w
        selected_monitor.height = log_h
        selected_monitor.x = mon_origin_x
        selected_monitor.y = mon_origin_y
        selected_monitor.phys_w = phys_w
        selected_monitor.phys_h = phys_h
        selected_monitor.relative_scale = target_scale

        if printStatements:
            print(f"Detected monitor: {selected_monitor.name} at ({selected_monitor.x}, {selected_monitor.y})")

    # Unpack coordinates
    x, y = coordinates

    # Reverse scale the coordinates
    adjusted_x, adjusted_y = stretchCoordsHELPER(x, y, selected_monitor)

    # Handle windowed mode adjustment
    if is_windowed:
        adjusted_y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates by adding the monitor's offset
    global_x = adjusted_x + selected_monitor.x
    global_y = adjusted_y + selected_monitor.y

    # Debugging print statements
    if printStatements:
        print(f"Adjusted Coordinates: ({adjusted_x}, {adjusted_y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Move the mouse
    pyautogui.moveTo(global_x, global_y, duration=duration)
    if printStatements:
        print(f"Moved to global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

# "Letterbox functions" (the below 3) adjust input coords by scaling and offsetting them instead of stretching them.
# Example: All in-game coordinates were recorded in a 16:9 space (x: 0-3840, y: 0-2160). If the current monitor has a different 
# aspect ratio (like 9:24), these functions scale coordinates to maintain correct positions within a centered 16:9 UI.
# This is generally called letterboxing handling: Think of black bars on top/bottom of a tall monitor to fit a white 16X9 rectangle,
# where the black bars are not valid coordinate spots, and the white rectangle is the area the coordinates are scaled to.
#FindMousePos_Letterbox   FindMousePos_Letterbox   FindMousePos_Letterbox   FindMousePos_Letterbox   FindMousePos_Letterbox   
def letterboxCoordsHELPER(x, y, monitor):
    """
    Reverse scale coordinates from 3840x2160 theoretical space to the monitor's dimensions.
    Adjust for windowed mode, and ensure the 16x9 rectangle is centered on the monitor.
    """
    global is_windowed


    # Determine monitor dimensions, adjust for windowed mode
    monitor_width = monitor.width
    monitor_height = monitor.height - is_windowed_px if is_windowed else monitor.height

    # Calculate the target 16x9 rectangle dimensions to fit within the monitor
    target_width = monitor_width
    target_height = monitor_width * (9 / 16)

    # Check if height exceeds the monitor's height, adjust if needed
    if target_height > monitor_height:
        target_height = monitor_height
        target_width = monitor_height * (16 / 9)

    # Calculate the offsets to center the rectangle
    horizontal_offset = (monitor_width - target_width) / 2
    vertical_offset = (monitor_height - target_height) / 2

    # Scale the coordinates to the target rectangle dimensions
    actual_x = (x / 3840) * target_width + horizontal_offset
    actual_y = (y / 2160) * target_height + vertical_offset

    return round(actual_x), round(actual_y)

def clickFuncLetterbox(coordinates, selected_monitor=None, printStatements=True):
    global is_windowed

    # Auto-detect monitor if not provided
    if selected_monitor is None:
        if printStatements:
            print("DEBUG: No monitor selected. Detecting monitor under mouse...")

        # Get monitor details
        details = get_monitor_details_under_mouse()

        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine monitor origin using handle
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

        # Wrap details into a simple object with attributes
        class MonitorObj:
            pass

        selected_monitor = MonitorObj()
        selected_monitor.name = mon_name
        selected_monitor.width = log_w
        selected_monitor.height = log_h
        selected_monitor.x = mon_origin_x
        selected_monitor.y = mon_origin_y
        selected_monitor.phys_w = phys_w
        selected_monitor.phys_h = phys_h
        selected_monitor.relative_scale = target_scale

        if printStatements:
            print(f"Detected monitor: {selected_monitor.name} at ({selected_monitor.x}, {selected_monitor.y})")

    # Unpack coordinates
    x, y = coordinates

    # Reverse scale the coordinates using your scaling function
    adjusted_x, adjusted_y = letterboxCoordsHELPER(x, y, selected_monitor)

    # Adjust for windowed mode if necessary
    if is_windowed:
        adjusted_y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates
    global_x = adjusted_x + selected_monitor.x
    global_y = adjusted_y + selected_monitor.y

    # Debug prints
    if printStatements:
        print(f"Adjusted Coordinates: ({adjusted_x}, {adjusted_y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Click the mouse
    pyautogui.click(global_x, global_y)
    if printStatements:
        print(f"Moved to global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

def moveToFuncLetterbox(coordinates, duration=0.8, selected_monitor=None, printStatements=True):
    global is_windowed

    # Auto-detect monitor if not provided
    if selected_monitor is None:
        if printStatements:
            print("DEBUG: No monitor selected. Detecting monitor under mouse...")

        # Get monitor details
        details = get_monitor_details_under_mouse()

        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine monitor origin using handle
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

        # Wrap details into a simple object with attributes
        class MonitorObj:
            pass

        selected_monitor = MonitorObj()
        selected_monitor.name = mon_name
        selected_monitor.width = log_w
        selected_monitor.height = log_h
        selected_monitor.x = mon_origin_x
        selected_monitor.y = mon_origin_y
        selected_monitor.phys_w = phys_w
        selected_monitor.phys_h = phys_h
        selected_monitor.relative_scale = target_scale

        if printStatements:
            print(f"Detected monitor: {selected_monitor.name} at ({selected_monitor.x}, {selected_monitor.y})")

    # Unpack coordinates
    x, y = coordinates

    # Reverse scale the coordinates using your scaling function
    adjusted_x, adjusted_y = letterboxCoordsHELPER(x, y, selected_monitor)

    # Adjust for windowed mode if necessary
    if is_windowed:
        adjusted_y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates
    global_x = adjusted_x + selected_monitor.x
    global_y = adjusted_y + selected_monitor.y

    # Debug prints
    if printStatements:
        print(f"Adjusted Coordinates: ({adjusted_x}, {adjusted_y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Move the mouse
    pyautogui.moveTo(global_x, global_y, duration=duration)
    if printStatements:
        print(f"Moved to global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

# "RawOffset" functions (the below 2) use unpopular UI, often using exact pixel offsets based off the edge of your monitor, instead 
# of using more traditional stretching/scaling methods. One example where this is used is Trackmania, where a new window prompt opens
# asking the user to specify the kind of AVI file they want to write.
# HOWEVER, the below two functions do not account for windows' scaling. Or mouseOverMonitor detection. That is next.
def clickFuncRawOffset(coordinates, selected_monitor=None, printStatements=True):
    global is_windowed
    if selected_monitor is None:
        print(f"Pass the selected_monitor var in your function")

    x, y = coordinates

    # Handle windowed mode adjustment
    if is_windowed:
        y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates by adding the monitor's offset
    global_x = x + selected_monitor.x
    global_y = y + selected_monitor.y

    # Debugging print statement to show everything clearly
    if printStatements is True:
        print(f"Adjusted Coordinates: ({x}, {y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Perform the click
    pyautogui.click(global_x, global_y)
    if printStatements is True:
        print(f"Clicked at global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

def moveToFuncRawOffset(coordinates, duration=0.8, selected_monitor=None, printStatements=True):
    global is_windowed
    if selected_monitor is None:
        print(f"Pass the selected_monitor var in your function")


    x, y = coordinates

    # Handle windowed mode adjustment
    if is_windowed:
        y += is_windowed_px  # Add back the 40px removed in windowed mode

    # Convert to global coordinates by adding the monitor's offset
    global_x = x + selected_monitor.x
    global_y = y + selected_monitor.y

    # Debugging print statement to show everything clearly
    if printStatements is True:
        print(f"Adjusted Coordinates: ({x}, {y})")
        print(f"Global Coordinates (Final): ({global_x}, {global_y})")

    # Move the mouse to the calculated global coordinates
    pyautogui.moveTo(global_x, global_y, duration=duration)  # Moves the mouse with the given duration
    if printStatements is True:
        print(f"Moved to global coordinates: ({global_x}, {global_y}) on Monitor: {selected_monitor.name}")

# The below 5 objects account for windows' scaling of specific UI elements. It's insane. Call the below 2 for game functions.
# Additionally, the below functions count true pixels of your monitor: If you try to move your mouse to a sub-pixel (which is possible
# because of windows scaling) Windows will auto-move the mouse to a "true" pixel on the displayed frame, throwing off calculations.
# The below functions account for this, making for DPI-aware mouse moving functions.
#FindMousePos_WithWindowsScaling3   FindMousePos_WithWindowsScaling3   FindMousePos_WithWindowsScaling3   FindMousePos_WithWindowsScaling3   
def clickFuncRawOffsetWindowsScaling(coordinates, selected_monitor=None, printStatements=True, bypass_scaling=False):
    """
    Moves to absolute coordinates relative to a monitor's origin.
    Uses the monitor the mouse is currently hovering over!!! Can work by passing selected_monitor too.
    Correctly calculates DPI using stupid logic.
    Windows only... sorry!
    Use bypass_scaling FALSE PRETTY MUCH ALL OF THE TIME. It's complicated I can't really explain it
    """
    global is_windowed

    # 1. Get System Base Scale (Context)
    base_scale = get_system_base_scale()

    x, y = coordinates
    
    # Placeholders for data gathering
    target_scale = 1.0
    mon_origin_x = 0
    mon_origin_y = 0
    mon_name = "Unknown"
    log_w, log_h = 0, 0
    phys_w, phys_h = 0, 0

    # --- CASE A: Auto-Detect (No Monitor provided) ---
    if selected_monitor is None:
        if printStatements: print("DEBUG: No monitor selected. Detecting monitor under mouse...")
        
        # Use Helper
        details = get_monitor_details_under_mouse()
        
        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine Origin using the handle from details
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

    # --- CASE B: Specific Monitor Object Provided ---
    else:
        if isinstance(selected_monitor, (int, float)):
            print(f"CRITICAL ERROR: 'selected_monitor' is a number. Pass the Monitor Object.")
            return

        mon_name = selected_monitor.name
        mon_origin_x = selected_monitor.x
        mon_origin_y = selected_monitor.y
        log_w = selected_monitor.width
        log_h = selected_monitor.height

        # We must query the Driver (Truth) specifically for this monitor name
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success = ctypes.windll.user32.EnumDisplaySettingsW(mon_name, -1, ctypes.byref(dm))
        
        if success:
            phys_w = dm.dmPelsWidth
            phys_h = dm.dmPelsHeight
            if log_w > 0:
                target_scale = phys_w / log_w
        else:
            if printStatements: print(f"ERROR: Could not query driver for {mon_name}")

    # 2. Handle Windowed Mode
    try:
        if is_windowed:
            y += is_windowed_px 
    except NameError:
        pass 

    # 3. Logic: Coordinate Scaling
    if bypass_scaling:
        # User says inputs are RAW (already scaled correctly for physical screen)
        # So we use them as-is relative to origin
        final_local_x = int(x)
        final_local_y = int(y)
        mode_str = "RAW (No Division)"
    else:
        # Inputs are Physical, but PyAutoGUI needs Logical
        final_local_x = int(x / target_scale)
        final_local_y = int(y / target_scale)
        mode_str = f"SCALED (Divided by {target_scale:.2f})"

    # 4. Global Calculation
    global_x = mon_origin_x + final_local_x
    global_y = mon_origin_y + final_local_y

    # 5. Exact Printing Format
    if printStatements:
        total_abs_scale = base_scale * target_scale
        
        print("="*60)
        print(f"DEBUG: Move To on Monitor [{mon_name}]")
        print(f"  > System Base Scale (Primary): {base_scale:.2f} ({(base_scale*100):.0f}%)")
        print(f"  > Monitor Stats:")
        print(f"      Logical (Virtual):  {log_w} x {log_h}")
        print(f"      Physical (Real):    {phys_w} x {phys_h}")
        print(f"  > Relative Scale (Phys/Log):   {target_scale:.2f}")
        print(f"  > Total Absolute Scale:        {total_abs_scale:.2f} ({(total_abs_scale*100):.0f}%)")
        print("-" * 30)
        print(f"  > Mode:                        {mode_str}")
        print(f"  > Input Local:                 ({x}, {y})")
        print(f"  > Final Global Target:         ({global_x}, {global_y})")
        print("="*60)

    # 6. Execute
    pyautogui.click(global_x, global_y)

def moveToFuncRawOffsetWindowsScaling(coordinates, duration=0.8, selected_monitor=None, printStatements=True, bypass_scaling=False):
    """
    Moves to absolute coordinates relative to a monitor's origin.
    Correctly calculates DPI using stupid logic.
    Windows only... sorry!
    Use bypass_scaling FALSE PRETTY MUCH ALL OF THE TIME. It's complicated I can't really explain it
    """
    global is_windowed

    # 1. Get System Base Scale (Context)
    base_scale = get_system_base_scale()

    x, y = coordinates
    
    # Placeholders for data gathering
    target_scale = 1.0
    mon_origin_x = 0
    mon_origin_y = 0
    mon_name = "Unknown"
    log_w, log_h = 0, 0
    phys_w, phys_h = 0, 0

    # --- CASE A: Auto-Detect (No Monitor provided) ---
    if selected_monitor is None:
        if printStatements: print("DEBUG: No monitor selected. Detecting monitor under mouse...")
        
        # Use Helper
        details = get_monitor_details_under_mouse()
        
        mon_name = details["name"]
        target_scale = details["relative_scale"]
        log_w, log_h = details["log_w"], details["log_h"]
        phys_w, phys_h = details["phys_w"], details["phys_h"]

        # Determine Origin using the handle from details
        mi = MONITORINFOEXW()
        mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
        ctypes.windll.user32.GetMonitorInfoW(details["handle"], ctypes.byref(mi))
        mon_origin_x = mi.rcMonitor.left
        mon_origin_y = mi.rcMonitor.top

    # --- CASE B: Specific Monitor Object Provided ---
    else:
        if isinstance(selected_monitor, (int, float)):
            print(f"CRITICAL ERROR: 'selected_monitor' is a number. Pass the Monitor Object.")
            return

        mon_name = selected_monitor.name
        mon_origin_x = selected_monitor.x
        mon_origin_y = selected_monitor.y
        log_w = selected_monitor.width
        log_h = selected_monitor.height

        # We must query the Driver (Truth) specifically for this monitor name
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success = ctypes.windll.user32.EnumDisplaySettingsW(mon_name, -1, ctypes.byref(dm))
        
        if success:
            phys_w = dm.dmPelsWidth
            phys_h = dm.dmPelsHeight
            if log_w > 0:
                target_scale = phys_w / log_w
        else:
            if printStatements: print(f"ERROR: Could not query driver for {mon_name}")

    # 2. Handle Windowed Mode
    try:
        if is_windowed:
            y += is_windowed_px 
    except NameError:
        pass 

    # 3. Logic: Coordinate Scaling
    if bypass_scaling:
        # User says inputs are RAW (already scaled correctly for physical screen)
        # So we use them as-is relative to origin
        final_local_x = int(x)
        final_local_y = int(y)
        mode_str = "RAW (No Division)"
    else:
        # Inputs are Physical, but PyAutoGUI needs Logical
        final_local_x = int(x / target_scale)
        final_local_y = int(y / target_scale)
        mode_str = f"SCALED (Divided by {target_scale:.2f})"

    # 4. Global Calculation
    global_x = mon_origin_x + final_local_x
    global_y = mon_origin_y + final_local_y

    # 5. Exact Printing Format
    if printStatements:
        total_abs_scale = base_scale * target_scale
        
        print("="*60)
        print(f"DEBUG: Move To on Monitor [{mon_name}]")
        print(f"  > System Base Scale (Primary): {base_scale:.2f} ({(base_scale*100):.0f}%)")
        print(f"  > Monitor Stats:")
        print(f"      Logical (Virtual):  {log_w} x {log_h}")
        print(f"      Physical (Real):    {phys_w} x {phys_h}")
        print(f"  > Relative Scale (Phys/Log):   {target_scale:.2f}")
        print(f"  > Total Absolute Scale:        {total_abs_scale:.2f} ({(total_abs_scale*100):.0f}%)")
        print("-" * 30)
        print(f"  > Mode:                        {mode_str}")
        print(f"  > Input Local:                 ({x}, {y})")
        print(f"  > Final Global Target:         ({global_x}, {global_y})")
        print("="*60)

    # 6. Execute
    pyautogui.moveTo(global_x, global_y, duration=duration)

def moveMouseRelativeScaled_Eh(movement_delta, selected_monitor=None, button='right', delay=0.055, printStatements=True):
    """
    Moves the mouse relative to current position using a segmented step loop.
    Uses LOW-LEVEL 'mouse_event'.
    
    Since we are using mouse_event (Raw Input), we NO LONGER need to scale 
    the input by DPI. 1 unit in mouse_event ~= 1 Physical Pixel.
    """
    
    # --- NEW HELPER: RAW RELATIVE MOVE ---
    def raw_relative_move(dx, dy):
        # MOUSEEVENTF_MOVE = 0x0001
        ctypes.windll.user32.mouse_event(0x0001, int(dx), int(dy), 0, 0)

    # --- CONFIGURATION VAR ---
    # Since we are raw, 100 here means exactly 100 physical pixels on screen.
    PIXELS_PER_STEP = 10

    # 1. Get System Context (Base Scale) - Used for Logging Only now
    base_scale = get_system_base_scale()

    # 2. Determine Monitor Details - Used for Logging Only now
    mon_name = "Unknown"
    log_w, log_h = 0, 0
    phys_w, phys_h = 0, 0
    relative_scale = 1.0

    # --- CASE A: Auto-Detect ---
    if selected_monitor is None:
        details = get_monitor_details_under_mouse()
        mon_name = details["name"]
        log_w = details["log_w"]
        log_h = details["log_h"]
        phys_w = details["phys_w"]
        phys_h = details["phys_h"]
        relative_scale = details["relative_scale"]

    # --- CASE B: Specific Monitor ---
    else:
        mon_name = selected_monitor.name
        log_w = selected_monitor.width
        log_h = selected_monitor.height
        
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success = ctypes.windll.user32.EnumDisplaySettingsW(mon_name, -1, ctypes.byref(dm))
        
        if success:
            phys_w = dm.dmPelsWidth
            phys_h = dm.dmPelsHeight
            if log_w > 0:
                relative_scale = phys_w / log_w
        else:
            if printStatements: print(f"ERROR: Could not query driver for {mon_name}")

    # 3. Calculate Distance
    # CRITICAL CHANGE: We trust the input is Physical. 
    # mouse_event takes Physical. No scaling division/multiplication needed.
    req_x, req_y = movement_delta
    
    target_x_total = int((req_x / base_scale / relative_scale))
    target_y_total = int((req_y / base_scale / relative_scale))

    # 4. Prints
    if printStatements:
        print("="*60)
        print(f"DEBUG: Relative Step-Move on [{mon_name}]")
        print(f"  > System Base Scale:           {base_scale:.2f}")
        print(f"  > Relative Scale:              {relative_scale:.4f}")
        print("-" * 30)
        print(f"  > Input Delta (Physical):      ({req_x}, {req_y})")
        print(f"  > Target (Raw Mickeys):        ({target_x_total}, {target_y_total})")
        print(f"  > Step Size:                   {PIXELS_PER_STEP} px")
        print("="*60)

    # 5. Helper Function (Raw Loop)
    def process_axis(total_pixels, is_x_axis):
        if total_pixels == 0:
            return

        direction = 1 if total_pixels > 0 else -1
        magnitude = abs(total_pixels)
        
        full_loops = magnitude // PIXELS_PER_STEP
        remainder = magnitude % PIXELS_PER_STEP
        
        step_val = PIXELS_PER_STEP * direction
        rem_val = remainder * direction
        
        # Execute Full Steps
        for _ in range(full_loops):
            if is_x_axis:
                raw_relative_move(step_val, 0)
            else:
                raw_relative_move(0, step_val)
            time.sleep(delay)
            
        # Execute Remainder
        if remainder > 0:
            if is_x_axis:
                raw_relative_move(rem_val, 0)
            else:
                raw_relative_move(0, rem_val)
            time.sleep(delay)

    # 6. Execution
    if button:
        pyautogui.mouseDown(button=button)
        time.sleep(0.2)
    
    try:
        process_axis(target_x_total, True)
        process_axis(target_y_total, False)
        
    finally:
        if button:
            time.sleep(0.2)
            pyautogui.mouseUp(button=button)
            
    if printStatements:
        print("Movement Complete.\n")

def moveMouseRelativeScaled(movement_delta, selected_monitor=None, button='right', delay=0.045, printStatements=True):
    """
    Moves the mouse relative to current position using a segmented step loop.
    
    The "delay" should be quadruple your framerate in certain circumstances (1 / (FPS * 4)) 
    This is to account for dropped frames, and how games interpret mouse movement. 

    The Step Size is normalized against the Total Absolute Scale (System + Monitor),
    ensuring '50px' represents the same visual/physical magnitude on all screens.

    DPI scaling on monitors is accounted for. Thanks stackOverflow.
    This is a Windows-exclusive function because of that, though.

    The step size is quantized to align with the TARGET MONITOR'S physical pixel grid
    (Relative Scale Denominator). 
    This ensures every logical step translates to a whole integer physical move,
    preventing Windows from discarding sub-pixel remainders.
    """

    # --- CONFIGURATION VAR ---
    # Target visual distance per step (in physical pixels)
    # We will round this to the nearest "Safe Grid" multiple.
    PIXELS_PER_STEP_TARGET = 100

    # 1. Get System Context (Base Scale)
    base_scale = get_system_base_scale()

    # 2. Determine Monitor Details
    mon_name = "Unknown"
    log_w, log_h = 0, 0
    phys_w, phys_h = 0, 0
    relative_scale = 1.0

    # --- CASE A: Auto-Detect ---
    if selected_monitor is None:
        details = get_monitor_details_under_mouse()
        mon_name = details["name"]
        log_w = details["log_w"]
        log_h = details["log_h"]
        phys_w = details["phys_w"]
        phys_h = details["phys_h"]
        relative_scale = details["relative_scale"]

    # --- CASE B: Specific Monitor ---
    else:
        mon_name = selected_monitor.name
        log_w = selected_monitor.width
        log_h = selected_monitor.height
        
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success = ctypes.windll.user32.EnumDisplaySettingsW(mon_name, -1, ctypes.byref(dm))
        
        if success:
            phys_w = dm.dmPelsWidth
            phys_h = dm.dmPelsHeight
            if log_w > 0:
                relative_scale = phys_w / log_w
        else:
            if printStatements: print(f"ERROR: Could not query driver for {mon_name}")

    # 3. Calculate Total Logical Distance
    req_x, req_y = movement_delta
    safe_scale = relative_scale if relative_scale > 0 else 1.0
    
    target_x_total = int(req_x / safe_scale)
    target_y_total = int(req_y / safe_scale)

    # --- 4. CALCULATE MONITOR-ALIGNED STEP LIMIT ---
    
    # A. Determine "Safe Logical Multiple" based on RELATIVE SCALE
    # Example: Scale 0.857 (6/7) -> Denominator 7 is the safe block.
    # Moving 7 logical pixels = Exactly 6 physical pixels.
    frac = Fraction(relative_scale).limit_denominator(1000)
    safe_multiple = frac.denominator
    
    # B. Calculate Raw Logical Step needed to hit Target Visual Magnitude
    total_abs_scale = base_scale * relative_scale
    safe_total_scale = total_abs_scale if total_abs_scale > 0 else 1.0
    raw_step_pixels = int(PIXELS_PER_STEP_TARGET / safe_total_scale)
    
    # C. Force Rounding to Nearest Safe Multiple
    remainder_step = raw_step_pixels % safe_multiple
    
    if remainder_step < (safe_multiple / 2):
        adjusted_step_pixels = raw_step_pixels - remainder_step
    else:
        adjusted_step_pixels = raw_step_pixels + (safe_multiple - remainder_step)

    # Safety: Must be at least one "Safe Block" size
    if adjusted_step_pixels < safe_multiple:
        adjusted_step_pixels = safe_multiple

    # 5. Prints
    if printStatements:
        print("="*60)
        print(f"DEBUG: Relative Step-Move on [{mon_name}]")
        print(f"  > System Base Scale:           {base_scale:.2f}")
        print(f"  > Monitor Stats:               {log_w}x{log_h} (Log) | {phys_w}x{phys_h} (Phys)")
        print(f"  > Relative Scale:              {relative_scale:.4f} (Grid Alignment: {frac.numerator}/{frac.denominator})")
        print("-" * 30)
        print(f"  > Input Delta (Physical):      ({req_x}, {req_y})")
        print(f"  > Scaled Target (Logical):     ({target_x_total}, {target_y_total})")
        print(f"  > Raw Ideal Step:              {raw_step_pixels} logical pixels")
        print(f"  > Grid-Aligned Step:           {adjusted_step_pixels} logical pixels (Multiples of {safe_multiple})")
        print("="*60)

    # 6. Helper Function
    def process_axis(total_pixels, is_x_axis):
        if total_pixels == 0:
            return

        direction = 1 if total_pixels > 0 else -1
        magnitude = abs(total_pixels)
        
        # Use the GRID ALIGNED step limit
        full_loops = magnitude // adjusted_step_pixels
        remainder = magnitude % adjusted_step_pixels
        
        step_val = adjusted_step_pixels * direction
        rem_val = remainder * direction
        
        # Execute Full Steps (Now Integer-Safe on Monitor Grid)
        for _ in range(full_loops):
            if is_x_axis:
                pyautogui.move(step_val, 0)
            else:
                pyautogui.move(0, step_val)
            time.sleep(delay)
            
        # Execute Remainder
        if remainder > 0:
            if is_x_axis:
                pyautogui.move(rem_val, 0)
            else:
                pyautogui.move(0, rem_val)
            time.sleep(delay)

    # 7. Execution
    if button:
        pyautogui.mouseDown(button=button)
        time.sleep(0.2)
    
    try:
        process_axis(target_x_total, True)
        process_axis(target_y_total, False)
        
    finally:
        if button:
            time.sleep(0.2)
            pyautogui.mouseUp(button=button)
            
    if printStatements:
        print("Movement Complete.\n")



class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFlags", wintypes.DWORD),
                ("szDevice", ctypes.c_wchar * 32)]

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        
        # FIXED PADDING (16 bytes for the Union)
        ("dmUnionPadding", ctypes.c_byte * 16), 
        
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),  # Truth Width
        ("dmPelsHeight", wintypes.DWORD), # Truth Height
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
    ]

def get_system_base_scale():
    """
    Gets the 'System' DPI scaling. 
    This is usually the scale of the Primary Monitor.
    Example: Returns 1.75 if the primary is set to 175%.
    """
    try:
        # Get DC for the entire screen (NULL)
        hdc = ctypes.windll.user32.GetDC(0)
        # 88 = LOGPIXELSX (Logical pixels per inch in X dimension)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi / 96.0
    except:
        return 1.0

def get_monitor_details_under_mouse():
    """
    Returns a dictionary containing the 'Truth' (Physical) and 'Lies' (Logical)
    dimensions of the monitor under the mouse, and the calculated relative scale.
    """
    #print("called this function")
    # 1. Get Mouse Point
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    
    # 2. Get Monitor Handle
    hmonitor = ctypes.windll.user32.MonitorFromPoint(pt, 2) # 2 = MONITOR_DEFAULTTONEAREST
    
    # 3. Get Logical Bounds (Windows/Virtual)
    mi = MONITORINFOEXW()
    mi.cbSize = ctypes.sizeof(MONITORINFOEXW)
    success_info = ctypes.windll.user32.GetMonitorInfoW(hmonitor, ctypes.byref(mi))
    
    # Defaults
    details = {
        "handle": hmonitor,
        "name": "Unknown",
        "log_w": 0, "log_h": 0,
        "phys_w": 0, "phys_h": 0,
        "relative_scale": 1.0
    }

    if success_info:
        details["name"] = mi.szDevice
        details["log_w"] = mi.rcMonitor.right - mi.rcMonitor.left
        details["log_h"] = mi.rcMonitor.bottom - mi.rcMonitor.top
        
        # 4. Get Physical Resolution (Driver/Real)
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        success_dev = ctypes.windll.user32.EnumDisplaySettingsW(mi.szDevice, -1, ctypes.byref(dm))
        
        if success_dev:
            details["phys_w"] = dm.dmPelsWidth
            details["phys_h"] = dm.dmPelsHeight
            
            # 5. Calculate Scale (Physical / Logical)
            if details["log_w"] > 0:
                details["relative_scale"] = details["phys_w"] / details["log_w"]
    else:
        print("had an error")

    return details

# MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS
# MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS    MISC USEFUL FUNCTIONS
# INSTEAD OF MODIFYING THESE FUNCTIONS, CREATE NEW ONES. THESE ARE USED AMONG MULTIPLE GAMES, AND MODIFICATIONS CAN BREAK THEM.

# You can choose to ask this function, or assume the chosen monitor is below the user's mouse
def askMonitorPrompt(defaultChoice="NoOffset"):
    monitors = get_monitors()
    
    # --- 1. GET SYSTEM CONTEXT SCALE ---
    # This is the "Base" scale (e.g., 1.75) that Windows is forcing on the Python process.
    base_scale = get_system_base_scale()

    # --- 2. PRE-CALCULATE ACCURATE ATTRIBUTES ---
    monitor_data = []
    
    for m in monitors:
        # Defaults
        phys_w = m.width
        phys_h = m.height
        relative_scale = 1.0
        
        # Query Driver for "Truth" (Physical Resolution)
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        if ctypes.windll.user32.EnumDisplaySettingsW(m.name, -1, ctypes.byref(dm)):
            phys_w = dm.dmPelsWidth
            phys_h = dm.dmPelsHeight
            
            # Calculate Relative Scale (Physical / Logical)
            if m.width > 0:
                relative_scale = phys_w / m.width
        
        # --- CRITICAL FIX: CALCULATE TRUE ABSOLUTE SCALING ---
        # True Scale = (Physical / Logical) * System_Base_Scale
        total_absolute_scale = relative_scale * base_scale

        monitor_data.append({
            "obj": m,
            "phys_w": phys_w,
            "phys_h": phys_h,
            "area": phys_w * phys_h,
            "total_scale": total_absolute_scale
        })

    # --- 3. IDENTIFY DEFAULTS ---
    max_res_area = max(d["area"] for d in monitor_data) if monitor_data else 0
    high_res_indices = [i for i, d in enumerate(monitor_data) if d["area"] == max_res_area]
    leftmost_indices = [i for i, m in enumerate(monitors) if m.x == 0]

    default_index = 0
    if defaultChoice == "Res" and high_res_indices:
        default_index = high_res_indices[0] 
    elif leftmost_indices:
        default_index = leftmost_indices[0] 

    # --- 4. PRINT DETAILS ---
    for i, data in enumerate(monitor_data):
        monitor = data["obj"]
        phys_w = data["phys_w"]
        phys_h = data["phys_h"]
        final_scale = data["total_scale"]
        
        special_notes = []
        if monitor.x == 0:
            special_notes.append(f"{NEON_GREEN}No Offset{RESET}")
        if i in high_res_indices:
            special_notes.append(f"{GREEN}Highest Res{RESET}")

        # Format: Resolution (Physical) | Scale (Total Absolute)
        scale_pct = int(round(final_scale * 100))
        
        base_info = (f"Monitor {i}: {monitor.name} | "
                     f"Resolution: {NEON_BLUE}{phys_w}{RESET}x{LIGHT_BLUE}{phys_h}{RESET} | "
                     f"Scale: {GOLD}{final_scale:.2f} ({scale_pct}%){RESET} | "
                     f"Offset: ({monitor.x}, {monitor.y})")
        
        if special_notes:
            print(f"{base_info} ({' & '.join(special_notes)})") 
        else:
            print(base_info)

    # --- 5. INPUT LOGIC ---
    if len(monitors) == 1:
        monitor_choice_adj = 0
        print(f"One monitor detected. Automatically chosen.")
    else:
        while True:
            user_input = input(f"Select monitor your game is on ({GOLD}0-{len(monitors) - 1}{RESET}) [Default {GOLD}{default_index}{RESET}]: ")

            if user_input == "":
                monitor_choice_adj = default_index
                break
            
            try:
                choice = int(user_input)
                if 0 <= choice < len(monitors):
                    monitor_choice_adj = choice
                    break
                else:
                    print(f"Choice '{choice}' is out of range. Please try again.")
            except ValueError:
                print(f"Invalid input '{user_input}'. Please enter a number.")

    chosen_monitor = monitors[monitor_choice_adj]
    
    # Move cursor to center (Using Logical/Virtual coords for the move function)
    center_x = chosen_monitor.width // 2
    center_y = chosen_monitor.height // 2
    moveToFuncStretch((center_x, center_y), 0.5, chosen_monitor, False) 
    
    print(f"Cursor moved to center of chosen monitor.")
    return chosen_monitor

def write_text(text): # Call this to write text for any reason (fastest approach)
    safe_text = str(text).strip().replace('"', '')
    for char in text:
        keyboard_controller.press(char)
        keyboard_controller.release(char)

def write_text_with_suffix(text, index):
    suffix = generate_suffix(index)
    write_text(text + suffix)

def generate_suffix(index):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letter_index = index // 6  # Determine which letter to use
    number_index = index % 6   # Determine the number suffix (1-6)

    if letter_index < 26:
        letter = letters[letter_index]
    else:
        # If we exceed 'Z', use combinations like AA, AB, etc.
        letter1 = letters[(letter_index // 26) - 1]  # First letter of the combination
        letter2 = letters[letter_index % 26]         # Second letter of the combination
        letter = letter1 + letter2
    
    return f"_{letter}{number_index + 1}"

def compute_scale_to_fill(text1, text2, canvas_width=1920, canvas_height=1080):
    image_width = float(text1) * 2
    image_height = float(text2) * 2
    scale_w = canvas_width / image_width
    scale_h = canvas_height / image_height
    # Use the larger scale so the smaller side touches the canvas
    scale = max(scale_w, scale_h) * 100
    return scale



uiSpeed = 0.06
if len(sys.argv) > 1:

    command = sys.argv[1]
    if command == "1": #iteration 1 
        clickFuncRawOffsetWindowsScaling((280, 418), bypass_scaling=False, printStatements=False) #pos1 (anchor point)
        time.sleep(uiSpeed) #waits for UI to respond (maybe too quick)
        keyboard_controller.press(Key.ctrl)
        keyboard_controller.press('c')
        keyboard_controller.release('c')
        keyboard_controller.release(Key.ctrl)
        time.sleep(uiSpeed) #waits for UI to respond (maybe too quick)
        clipboard1 = pyperclip.paste()
        #compute height of input image (input X2)
        clickFuncRawOffsetWindowsScaling((376, 418), bypass_scaling=False, printStatements=False) #pos2 (anchor point 2)
        time.sleep(uiSpeed) #waits for UI to respond (maybe too quick)
        keyboard_controller.press(Key.ctrl)
        keyboard_controller.press('c')
        keyboard_controller.release('c')
        keyboard_controller.release(Key.ctrl)
        time.sleep(uiSpeed) #waits for UI to respond (maybe too quick)
        clipboard2 = pyperclip.paste()
        #print(f"{clipboard1}, {clipboard2}")


        scaleVal = compute_scale_to_fill(clipboard1, clipboard2) #compute width of input image  (input X2)
        clickFuncRawOffsetWindowsScaling((290, 296), bypass_scaling=False, printStatements=False) #scale (100)
        time.sleep(uiSpeed) #waits for UI to respond (maybe too quick)
        write_text(str(scaleVal))
        #pyautogui.keyDown('enter')
        #pyautogui.keyUp('enter')
        clickFuncRawOffsetWindowsScaling((94, 296), bypass_scaling=False, printStatements=False) #scale stopwatch

        #go to beginning of clip (AHK) /////////

        #call python file////////////////
        #see if anchor point is at expected spot (by clicking, copying, reading clipboard)
        #same for anchor point 2
        #if okay, click scale value. This is the before value. Apply scale as a percentage until image is at edge of frame
        #click scale stopwatch (applies keyframe)

        #go to end of clip (AHK)
        #call new python file (hi)

        #Read last 2 clipboard entries (is that possible?)
        #From that data, apply scale value based off a 2x zoom in on the image
        #end
        scaleValTwo = round(scaleVal * 2, 4)
        scaleValTwo = str(scaleValTwo)
        print(scaleValTwo)

    else: #iteration 2 for this specific function

        clickFuncRawOffsetWindowsScaling((290, 296), bypass_scaling=False, printStatements=False) #scale (float)
        time.sleep(uiSpeed) #waits for UI to respond
        write_text(str(command))
        time.sleep(uiSpeed) #waits for UI to respond
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
        time.sleep(uiSpeed) #waits for UI to respond
        moveToFuncRawOffsetWindowsScaling((1920, 1650), duration=0.01, bypass_scaling=False, printStatements=False) #centered
        write_text("v") #now selecting again
        #"mousePosBefore|ScalingCoords2X"
        time.sleep(uiSpeed) #waits for UI to respond