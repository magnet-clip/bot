import time
import random

def get_temp_file_name(): 
	return str(random.randint(10000, 99999)) + "_" + str(int(round(time.time() * 1000)))
