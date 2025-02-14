import subprocess
import multiprocessing

def run_seed_script(port):
    # Define the command to run the seed.py script with the specified port
    command = ['python', 'Peer/peer.py', '--port', str(port) , '--max-peers', '20']
    subprocess.run(command)
    print(f"Seed server started on port {port}")

if __name__ == '__main__':
    # Define the ports to run the script with
    ports = [3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009]
    # Create a list of processes
    processes = []

    for port in ports:
        process = multiprocessing.Process(target=run_seed_script, args=(port,))
        processes.append(process)
        process.start()  # Start the process

    # Wait for all processes to finish
    for process in processes:
        process.join()

    print("All Peer servers started.")
