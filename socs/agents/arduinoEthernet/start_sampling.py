import os
from ocs.ocs_client import OCSClient

# Set your target OCS environment realm
os.environ['OCS_REALM'] = 'test_realm'

# Hook into your active Arduino agent instance
client = OCSClient('arduino1')
#client = OCSClient('arduino-collector')


print("Requesting 'arduino instance' to start the 'sampling' process loop...")

# Fire the background acquisition routine
status, message, session = client.sampling.start()

print(f"Status: {status}")
print(f"Message: {message}")
