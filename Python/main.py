import random
from math import log

# Constants
Q_LIMIT = 100
BUSY = 1
IDLE = 0

# Global Variables
next_event_type = 0
num_custs_delayed = 0
num_delays_required = 0
num_events = 0
num_in_q = 0
server_status = IDLE
area_num_in_q = 0.0
area_server_status = 0.0
mean_interarrival = 0.0
mean_service = 0.0
sim_time = 0.0
time_arrival = [0.0] * (Q_LIMIT + 1)
time_last_event = 0.0
time_next_event = [0.0] * 3
total_of_delays = 0.0


# Initialize simulation variables
def initialize():
    global sim_time, server_status, num_in_q, time_last_event, num_custs_delayed, total_of_delays, area_num_in_q, area_server_status

    # Initialize the simulation clock
    sim_time = 0

    # Initialize the state variables.
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0

    # Initialize the statistical counters.
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0

    # Initialize event list.
    time_next_event[1] = sim_time + expon(mean_interarrival)
    time_next_event[2] = 1.0e+30


# Determine the next event and advance simulation time
def timing():
    global next_event_type, sim_time
    min_time_next_event = 1.0e+29
    next_event_type = 0
    # Determine the event type of the next event to occur.
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    # Check to see whether the event list is empty.
    if next_event_type == 0:
        # The event list is empty, so stop the simulation.
        print("\nEvent list empty at time", sim_time)
        exit(1)
    # The event list is not empty, so advance the simulation clock.
    sim_time = min_time_next_event


# Handle arrival event
def arrive():
    global num_in_q, server_status, total_of_delays, num_custs_delayed
    delay = 0.0
    # Schedule next arrival.
    time_next_event[1] = sim_time + expon(mean_interarrival)
    # Check to see whether server is busy.
    if server_status == BUSY:
        # Server is busy, so increment number of customers in queue.
        num_in_q += 1
        # Check to see whether an overflow condition exists.
        if num_in_q > Q_LIMIT:
            # The queue has overflowed, so stop the simulation.
            print("\nOverflow of the array time_arrival at {:.3f} time".format(sim_time), file=outputfile)
            exit(2)

        # Otherwise there is still room in the queue, so store the time of arrival of the
        # arriving customer at the (new) end of time_arrival.
        time_arrival[num_in_q] = sim_time
    else:
        # Server is idle, so arriving customer has a delay of zero.
        delay = 0.0
        total_of_delays += delay

        # Increment the number of customers delayed, and make server busy.
        num_custs_delayed += 1
        server_status = BUSY
        # Schedule a departure (service completion).
        time_next_event[2] = sim_time + expon(mean_service)


# Handle departure event
def depart():
    global num_in_q, server_status, total_of_delays, num_custs_delayed
    # Check to see whether the queue is empty.
    if num_in_q == 0:
        # The queue is empty so make the server idle and eliminate the
        # departure (service completion)

        server_status = IDLE
        time_next_event[2] = 1.0e+30
    else:
        # The queue is nonempty, so decrement the number of customers in queue.
        num_in_q -= 1
        # Compute the delay of the customer who is beginning service and update
        # the total delay accumulator.
        delay = sim_time - time_arrival[1]
        total_of_delays += delay

        # Increment the number of customers delayed, and schedule departure.
        num_custs_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service)

        # Move each customer in queue (if any) up one place.
        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]


# Generate Report
def report():
    global total_of_delays, num_custs_delayed, area_num_in_q, sim_time, area_server_status
    # Compute and write estimates of desired measures of performance.

    print("\n\nAverage delay in queue: {:.3f} minutes".format(total_of_delays / num_custs_delayed), file=outputfile)
    print("Average number in queue: {:.3f}".format(area_num_in_q / sim_time), file=outputfile)
    print("Server utilization: {:.3f}".format(area_server_status / sim_time), file=outputfile)
    print("Time simulation ended: {:.3f} minutes".format(sim_time), file=outputfile)


# Update area accumulators for time-average statistics.
def update_time_avg_stats():
    global area_num_in_q, area_server_status, time_last_event
    # Compute time since last event, and update last-event-time marker
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    # Update area under number-in-queue function.
    area_num_in_q += num_in_q * time_since_last_event

    # Update area under server-busy indicator function.
    area_server_status += server_status * time_since_last_event


# Exponential generation function.
def expon(mean):
    return -mean * log(random.random())


def main():
    global num_events, mean_interarrival, mean_service, num_delays_required, inputfile, outputfile
    # Open input and output files
    inputfile = open("mm1.in", 'r')
    outputfile = open("mm1.out", 'w')

    # Specify the number of events
    num_events = 2

    # Read input parameters
    mean_interarrival, mean_service, num_delays_required = map(float, inputfile.readline().split())
    print("Single-server queueing system\n", file=outputfile)
    print("Mean interarrival time: {:.3f} minutes\n".format(mean_interarrival), file=outputfile)
    print("Mean service time: {:.3f} minutes\n".format(mean_service), file=outputfile)
    print("Number of customers: {}\n".format(int(num_delays_required)), file=outputfile)

    # Initialize the simulation
    initialize()

    # Run the simulation while more delays are still needed
    while num_custs_delayed < num_delays_required:
        # Determine the next event
        timing()

        # Update time_average statistical accumulators
        update_time_avg_stats()

        # Invoke the appropriate function
        if next_event_type == 1:
            arrive()
        elif next_event_type == 2:
            depart()

    # Invoke the report generator and end the simulation
    report()

    inputfile.close()
    outputfile.close()


if __name__ == "__main__":
    main()
