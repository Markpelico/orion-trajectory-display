#!/usr/bin/env python
"""
Simple test script to verify connection to Trick Variable Server
and print out the Orion vehicle state data.
"""

import socket
import time
import sys


def test_connection(host="localhost", port=7108, duration=10):
    """
    Test connection to Trick Variable Server and print data.
    
    Args:
        host (str): Hostname or IP address
        port (int): Port number
        duration (int): How long to run the test (seconds)
    """
    print("="*70)
    print("Trick Variable Server Connection Test")
    print("="*70)
    print("Host: {}".format(host))
    print("Port: {}".format(port))
    print("Duration: {} seconds".format(duration))
    print("="*70)
    
    try:
        # Create socket and connect
        print("\n[1/4] Creating socket...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        print("[2/4] Connecting to Trick Variable Server...")
        client_socket.connect((host, port))
        print("      SUCCESS! Connected to {}:{}".format(host, port))
        
        # Create file reader
        src = client_socket.makefile("r")
        
        # Pause and clear variables
        print("[3/4] Configuring variable server...")
        client_socket.send(b"trick.var_pause()\n")
        client_socket.send(b"trick.var_clear()\n")
        
        # Add the Orion state variables
        trick_vars = [
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[2]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[2]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[2]",
            "Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch"
        ]
        
        for var in trick_vars:
            cmd = "trick.var_add(\"{}\")\n".format(var)
            client_socket.send(cmd.encode())
        
        # Unpause to start receiving data
        client_socket.send(b"trick.var_unpause()\n")
        print("      SUCCESS! Variables configured")
        
        print("[4/4] Reading data from Trick Variable Server...")
        print("="*70)
        print("\nReceiving data (Ctrl+C to stop):\n")
        
        # Read and display data
        start_time = time.time()
        count = 0
        
        while True:
            # Check if duration exceeded
            if time.time() - start_time > duration:
                print("\n\nTest duration reached. Stopping...")
                break
            
            # Read line from server
            data = src.readline()
            
            if data == '':
                print("WARNING: No data received. Is the simulation running?")
                time.sleep(1)
                continue
            
            # Parse data
            values = data.strip().split("\t")
            
            if len(values) >= 10:
                count += 1
                
                # Extract values
                pos_x = float(values[1])
                pos_y = float(values[2])
                pos_z = float(values[3])
                vel_x = float(values[4])
                vel_y = float(values[5])
                vel_z = float(values[6])
                acc_x = float(values[7])
                acc_y = float(values[8])
                acc_z = float(values[9])
                utc_sec = float(values[10])
                
                # Print every 10th reading to avoid spam
                if count % 10 == 0:
                    print("Sample #{} at t={:.2f}s:".format(count, utc_sec))
                    print("  Position (m):     X={:+.4e}  Y={:+.4e}  Z={:+.4e}".format(pos_x, pos_y, pos_z))
                    print("  Velocity (m/s):   X={:+.4e}  Y={:+.4e}  Z={:+.4e}".format(vel_x, vel_y, vel_z))
                    print("  Accel (m/s^2):    X={:+.4e}  Y={:+.4e}  Z={:+.4e}".format(acc_x, acc_y, acc_z))
                    print()
            else:
                print("WARNING: Received incomplete data (got {} values, expected 10+)".format(len(values)))
        
        # Clean up
        print("\n" + "="*70)
        print("Test Summary:")
        print("  Total samples received: {}".format(count))
        print("  Average rate: {:.1f} Hz".format(count / duration))
        print("="*70)
        print("\nCleaning up...")
        client_socket.send(b"trick.var_pause()\n")
        client_socket.send(b"trick.var_clear()\n")
        client_socket.close()
        print("Connection closed successfully.")
        print("\n✓ TEST PASSED - Connection and data retrieval working!")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        try:
            client_socket.send(b"trick.var_pause()\n")
            client_socket.send(b"trick.var_clear()\n")
            client_socket.close()
        except:
            pass
        print("Connection closed.")
        
    except socket.error as e:
        print("\n✗ CONNECTION FAILED!")
        print("Socket error: {}".format(e))
        print("\nPossible reasons:")
        print("  1. Trick simulation is not running")
        print("  2. Incorrect host or port")
        print("  3. Firewall blocking connection")
        print("  4. Simulation not in RUN mode")
        return False
        
    except Exception as e:
        print("\n✗ TEST FAILED!")
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Default values
    host = "localhost"
    port = 7108
    duration = 10
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        duration = int(sys.argv[3])
    
    # Run test
    success = test_connection(host, port, duration)
    
    if success:
        print("\nYou can now run the full trajectory display:")
        print("  python flight_trajectory_display.py {} {}".format(host, port))
    else:
        print("\nPlease fix the connection issues before running the full display.")
    
    sys.exit(0 if success else 1)

