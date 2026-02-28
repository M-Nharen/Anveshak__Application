import serial
import numpy as np
import threading
import time

# Simulation of virtual serial ports

# Mac: First install socat using, brew install socat
# Run the following command in the terminal and keep it running on the execution of code
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
# You can find the port names in the terminal where you ran the socat command. 

# Windows: In this application, we are going to use com0com
# There will a zip file attched to the resouces of the application. Run setup.exe
# Open your installed folder, run setupc.exe
# Type: install PortName=COM30 PortName=COM31 to create your virtual ports

# Replace "your_port" with the port name of the sender and receiver

# To install dependencies, 
# pip install pyserial
# pip install numpy

# Now to run your code, 
# python3 application.py

port_sender = "/dev/pts/8"  
port_receiver = "/dev/pts/9" 

BYTE_RESET_PROBABLITY = 0.005

def send_data(ser: serial.Serial, data: np.ndarray) -> None:

    header = [0xAA, 0x55]
    payload = data.tolist()
    checksum = sum(payload) % 256
    
    data_to_send = header + payload + [checksum]

    for b in data_to_send:
        ser.write(bytes([b]))

    # Your code to send the data
    # Input: your pwm numpy array
    # TASK: write the data to the port_sender
    # You are not allowed to use any functions other than ser.write() to send the data 
    # You must send the data in bytes format, and only one byte can be sent at a time

    # For challenge question, uncomment this
    # This should be done, JUST before sending the data
    # No other code should be there after this, other than sending the data itself

    # for i in range(len(data_to_send)):
    #     if np.random.random() < BYTE_RESET_PROBABLITY:
    #         data_to_send[i] = 0x00

def receive_data(ser: serial.Serial) -> tuple[np.ndarray, bool]:

    received_pwm_data = np.array([])
    acknowledgement = False

    while True:
        b1 = ser.read(1)
        if not b1: return received_pwm_data, False
        if ord(b1) == 0xAA:
            b2 = ser.read(1)
            if b2 and ord(b2) == 0x55:
                break

    raw_payload = ser.read(100)
    if len(raw_payload) < 100:
        return received_pwm_data, False

    raw_checksum = ser.read(1)
    if not raw_checksum:
        return received_pwm_data, False
    
    received_checksum = ord(raw_checksum)

    payload_list = list(raw_payload)
    calculated_checksum = sum(payload_list) % 256
    
    if calculated_checksum == received_checksum:
        received_pwm_data = np.array(payload_list)
        acknowledgement = True
    
    return received_pwm_data, acknowledgement

    # Your code to receive the data
    # Output: your PWM array, and the acknowledgement of the data transmission
    # TASK: receive data from the port_receiver
    # You are not allowed to use any functions other than ser.read() to receive the data
    # You must read the data in bytes format, one by one, and convert it back to the original data format
    # You should have a mechanism to check if the transmission of the data is properly done
    # If yes, set the acknowledgement to True, else False

def receive_thread_task(received_data: list, no_of_success: int):
    no_of_tries = 0
    try:
        with serial.Serial(port_receiver, 9600, timeout=0.2) as ser:
            while len(received_data) < 100 and no_of_tries < 150:
                print(f"[RECIEVER] [{no_of_tries}] Trying to Recieve Data")

                received_arr, acknowledgement = receive_data(ser)
                
                if np.any(received_arr) or acknowledgement:
                    received_data.append(received_arr)
                    if acknowledgement:
                        print(f"[RECEIVER] [{len(received_data)}] SUCCESS")
                        no_of_success[0] += 1
                    else: 
                        print(f"[RECEIVER] [{len(received_data)}] FAILED")
                no_of_tries += 1
                time.sleep(0.01) 
            else: 
                print(f"[RECEIVER] Time Out")
    except Exception as e:
        print(f"Receiver Thread Error: {e}")

def send_thread_task(all_data):
    try: 
        with serial.Serial(port_sender, 9600) as ser:
            for i, data in enumerate(all_data):
                send_data(ser, data)
                print(f"[SENDER]   [{i+1}] Packet Sent")
                time.sleep(0.15) 
    except Exception as e:
        print(f"Sender Thread Error: {e}")

def generate_pwm():

    pwm = np.random.randint(0, 255, size=(100,))
    return pwm

def main():

    pwm_data = [generate_pwm() for i in range(100)]
    received_data = []
    no_of_success = [0]

    receiver_thread = threading.Thread(target=receive_thread_task, args=(received_data, no_of_success))
    receiver_thread.daemon = True
    receiver_thread.start()

    time.sleep(1)

    sender_thread = threading.Thread(target=send_thread_task, args=(pwm_data,))
    sender_thread.daemon = True
    sender_thread.start()

    time.sleep(1)

    sender_thread.join(timeout=30)
    receiver_thread.join(timeout=30)

    print(f"Total Successful: {no_of_success[0]}/100")

if __name__ == "__main__":
    main()
