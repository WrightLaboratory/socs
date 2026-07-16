import time
import socket
import txaio
import os
from os import environ
from ocs import ocs_agent, site_config
from ocs.ocs_twisted import TimeoutLock
import argparse

class ArduinoSerialBridge:
    def __init__(self, agent, ip_address="192.168.1.2", port=80):
        self.agent = agent
        self.ip_address = ip_address
        self.port = port 
        self.log = agent.log
        self.lock = TimeoutLock(default_timeout=5)
        self.is_streaming = False

        # Register data feeds in the OCS system
        agg_params = { 'frame_length': 10 * 60 } # [sec]
        self.agent.register_feed('serial_lines', record=True, agg_params=agg_params, buffer_time=1.)

    @ocs_agent.param('state', default='L', type=str, choices=['H', 'L'])
    def set_pin_state(self, session, params):
        """OCS Task to instantly toggle Pin 9 to HIGH ('H') or LOW ('L')."""
        state = params['state']
        with self.lock.acquire_timeout(timeout=3, job='set_pin_state') as acquired:
            if not acquired:
                return False, "Lock acquisition timeout."
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((self.ip_address, self.port))
                s.send(state.encode('utf-8'))
                response = s.recv(1024).decode('utf-8').strip()
                s.close()
                return True, f"Sent command: {state}. Arduino response: {response}"
            except Exception as e:
                return False, f"Error: {e}"

    def start_sampling(self, session, params):
        """OCS Process to continuously read raw data from the Arduino."""
        if self.is_streaming:
            return False, "Sampling loop is already active."

        self.is_streaming = True
        session.set_status('running')
        self.log.info("Starting background loop to acquire raw Arduino telemetry...")

        while self.is_streaming:
            raw_data = ""
            try:
                # 1. Connect out to the Arduino Server with an explicit 2-second timeout
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)  # <-- Forces the socket to break and error instead of freezing
                s.connect((self.ip_address, self.port))
                
                s.sendall(b'R')
                time.sleep(0.1) # Give the Arduino time to finish responding.
                
                # 3. Gather the full text package
                raw_data = s.recv(1024).decode('utf-8').strip()
                s.close()

                # Log the raw text to expose exactly what is crossing the network
                self.log.info(f"DEBUG: Raw response string received: '{raw_data}'")

                # 4. Filter out any HTTP header data noise and find our comma values
                # Splits by line breaks and searches for a row containing a comma
                data_line = ""
                for line in raw_data.splitlines():
                    if "," in line:
                        data_line = line.strip()
                        break
                
                if data_line:
                    parts = data_line.replace(",", " ").split()
                    if len(parts) >= 17:
                        val_analog0 = float(parts[0])
                        val_analog1 = float(parts[1])
                        val_analog2 = float(parts[2])
                        val_analog3 = float(parts[3])
                        val_analog4 = float(parts[4])
                        val_analog5 = float(parts[5])
                        val_digital0 = float(parts[6])
                        val_digital1 = float(parts[7])
                        val_digital2 = float(parts[8])
                        val_digital3 = float(parts[9])
                        val_digital4 = float(parts[10])
                        val_digital5 = float(parts[11])
                        val_digital6 = float(parts[12])
                        val_digital7 = float(parts[13])
                        val_digital8 = float(parts[14])
                        val_digital9 = float(parts[15])

                        val_cablefake = float(parts[16])

                        # 5. Package for the OCS Influx Publisher
                        now = time.time()
                        message = {
                            'block_name': 'serial_data',
                            'timestamps': [now],
                            'data': {
                                'a0_reading': [val_analog0],
                                'a1_reading': [val_analog1],
                                'a2_reading': [val_analog2],
                                'a3_reading': [val_analog3],
                                'a4_reading': [val_analog4],
                                'a5_reading': [val_analog5],
                                'd0_reading': [val_digital0],
                                'd1_reading': [val_digital1],
                                'd2_reading': [val_digital2],
                                'd3_reading': [val_digital3],
                                'd4_reading': [val_digital4],
                                'd5_reading': [val_digital5],
                                'd6_reading': [val_digital6],
                                'd7_reading': [val_digital7],
                                'd8_reading': [val_digital8],
                                'd9_reading': [val_digital9],
                                'cable_fake_reading': [val_cablefake]
                            }
                        }

                        self.log.info(f"Publishing Metrics -> Analog0: {val_analog0}, FakeCable: {val_cablefake}")
                        self.agent.publish_to_feed('serial_lines', message)
                    else:
                        self.log.warn(f"Data row length mismatch. Expected 17 elements, got {len(parts)}.")
                else:
                    self.log.warn("No comma-separated data line found in the server response.")

            except Exception as e:
                self.log.warn(f"Telemetry loop update skipped: {e}")

            # Wait 2 seconds between polling sweeps
            time.sleep(2.0)

        session.set_status('stopping')
        return True, "Finished raw sampling loop."

    def stop_sampling(self, session, params):
        if self.is_streaming:
            self.is_streaming = False
            return True, 'Requested to stop taking data.'
        return False, 'Acquisition is not currently running'

def main(args=None):
    txaio.use_twisted()
    txaio.make_logger()
    txaio.start_logging(level=environ.get("LOGLEVEL", "info"))

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip-address', type=str, default='192.168.1.2', help="Arduino IP")
    parser.add_argument('--port', type=int, default=80, help="Arduino Server Port")
    parser.add_argument('--mode', type=str, default='countarduino', choices=['idle', 'countarduino'])

    args = site_config.parse_args(agent_class='ArduinoAgent', parser=parser, args=args)

    ip_addr = args.ip_address
    port_num = args.port

    agent, runner = ocs_agent.init_site_agent(args)
    bridge = ArduinoSerialBridge(agent, ip_address=ip_addr, port=port_num)

    # Register both the on-demand action task and the looping process
    agent.register_task('countarduino', bridge.set_pin_state)
    agent.register_process('sampling', bridge.start_sampling, bridge.stop_sampling)
    
    runner.run(agent, auto_reconnect=True)

if __name__ == '__main__':
    main()
