import sys
import os
from ocs.ocs_client import OCSClient

def toggle_led(state_choice):
    """
    Sends an 'H' or 'L' command to the arduino-collector OCS agent.
    
    Args:
        state_choice (str): 'H' for HIGH (LED ON), 'L' for LOW (LED OFF)
    """
    # 1. Point the client to your specific OCS realm layout if not already set globally
    os.environ['OCS_REALM'] = 'test_realm'
    
    # 2. Connect directly to your running instance ID from default.yaml
    client = OCSClient('arduino1')
    
    print(f"Targeting 'arduino1' agent. Setting state to: {state_choice}")
    
    try:
        # 3. Fire the 'count' task with your chosen parameter
        status, message, session = client.countarduino.start(state=state_choice)
        
        # 4. Print results from the OCS orchestration layer
        print(f"--- OCS Framework Response ---")
        print(f"Status Code/Result: {status}")
        print(f"Agent Log Message:  {message}")
        
    except Exception as e:
        print(f"Error communicating with OCS environment: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        chosen_input = sys.argv[1].upper()
        if chosen_input in ['H', 'L']:
            toggle_led(chosen_input)
        else:
            print("Invalid argument! Choose 'H' or 'L'.")
    else:
        print("Usage instructions:")
        print("  python toggle_control.py H   <- Turn LED ON")
        print("  python toggle_control.py L   <- Turn LED OFF")
