import pyautogui
import time
import keyboard

print("COORDINATE RECORDER")
print("Click on each point you want to record.")
print("Press ESC to finish recording.")

recorded_points = []

def on_click(x, y, button, pressed):
    if pressed:
        recorded_points.append((x, y))
        print(f"Recorded point #{len(recorded_points)}: X: {x}, Y: {y}")
    return True  # Continue listening

try:
    # Use pynput for better mouse event handling
    from pynput.mouse import Listener
    
    # Start listening for mouse clicks
    with Listener(on_click=on_click) as listener:
        while True:
            if keyboard.is_pressed('esc'):
                break
            time.sleep(0.1)
    
    # Print all recorded coordinates
    print("\nAll recorded coordinates:")
    for i, (x, y) in enumerate(recorded_points, 1):
        print(f"Click {i}: X: {x}, Y: {y}")
    
    # Format for direct copy-paste into code
    print("\nCode-ready format:")
    for i, (x, y) in enumerate(recorded_points, 1):
        print(f"# Click {i}")
        print(f"pyautogui.click(x={x}, y={y})")
        print(f"time.sleep(1.5)\n")
        
except ImportError:
    # Fallback method if pynput is not installed
    print("For better functionality, install pynput: pip install pynput")
    print("Using fallback method...")
    
    try:
        while True:
            if pyautogui.mouseDown():
                x, y = pyautogui.position()
                recorded_points.append((x, y))
                print(f"Recorded point #{len(recorded_points)}: X: {x}, Y: {y}")
                while pyautogui.mouseDown():
                    time.sleep(0.1)  # Wait for mouse release
            if keyboard.is_pressed('esc'):
                break
            time.sleep(0.1)
            
        # Print all recorded coordinates
        print("\nAll recorded coordinates:")
        for i, (x, y) in enumerate(recorded_points, 1):
            print(f"Click {i}: X: {x}, Y: {y}")
        
    except KeyboardInterrupt:
        print("\nRecording interrupted.")
    except Exception as e:
        print(f"Error: {e}")
        
print("\nDone recording coordinates.")