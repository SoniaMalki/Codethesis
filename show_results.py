import pickle
import os
from modules.experience import Experience

# dir_name = "experiences_results/experiences_results_CITTA_temp_new/"
# files = os.listdir(dir_name)
# files = [k for k in files if ".obj" in k]
# files.sort(reverse=True)
# filename = files[0]
# print(filename)
# with open("{}/{}".format(dir_name, filename), 'rb') as filepy:
#     experiences = pickle.load(filepy)
# print(experiences.taskset_list[0], experiences.taskset_assignment_result_list[0])



dir_name = "results/taskset"
filename = "taskset_custom.obj"
with open(dir_name+"/"+filename, 'rb') as filepy:
    res = pickle.load(filepy)

print(repr(res))

print("")
print("")
print(repr(res.taskset_set_list))

