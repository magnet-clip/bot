import time
import random
import os
import shutil

def get_temp_file_name(): 
	return str(random.randint(10000, 99999)) + "_" + str(int(round(time.time() * 1000)))

def clear_folder(folder):
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print(e)
