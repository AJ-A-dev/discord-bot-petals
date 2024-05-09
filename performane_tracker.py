import time

"""
time object and function for reseting it
"""

class PerformanceTracker:
    def __init__(self):
        self.start_time = time.time()
        self.delta_time = 0 # Time difference between updates
        self.time_from_start = 0 #tokens / s
        self.tokens_per_second = 0 #tokens / s
        self.speed_measurements = list() # List to hold individual speed measurements
        self.average_speed = 0 # Average processing speed
        self.pathfinding_time = None


    def get_delta_and_from_initial_time(self):
        """
        returns delta time and time from initial start
        """
        self.delta_time = time.time() - self.delta_time #time between each token
        self.time_from_start = time.time() - self.start_time #the whole time generating takes
        self.tokens_per_second = 1/self.delta_time if self.delta_time != 0 else 0 # get tokens/ s from delta time

        # get the time of pathfinding/time before it starts writing
        if not self.pathfinding_time: # first time
            self.pathfinding_time = self.time_from_start
        else:
            self.speed_measurements.append(self.delta_time) #appends to list for average speed at the end

        
    def update_delta_time(self):
        """goes at start of loop"""
        self.delta_time = time.time()

    def get_average_token_speed(self):
        """
        returns the average time of token speed goes after loop
        returns tokens / s

        this one is made for ollama because getting tokens the same way as for petals was not possible
        """
        try:
            self.average_speed = 1/(sum(self.speed_measurements)/(len(self.speed_measurements)))
        except ZeroDivisionError:
            self.average_speed = 1/(0.5)

        return self.average_speed

    def get_rough_average_from_whole_time(self, string):
        count = string
        punctuations = (".", ",", "?", "!", ";", ":")
        # Add space around each punctuation mark
        for p in punctuations:
            count = count.replace(p, f" {p} ")

        count = len(string.split(" "))
        if self.time_from_start > 0:
            self.average_speed = (count)/(self.time_from_start)
        else: 
            self.average_speed = (count)/(1)

        return self.average_speed
    

if __name__ == "__main__":
    time_handler = PerformanceTracker()
    for _ in range(30):
        time_handler.update_delta_time()
        time.sleep(0.5) # Simulate work by sleeping for half a second
        time_handler.get_delta_and_from_initial_time()
    print(time_handler.get_average_token_speed())
