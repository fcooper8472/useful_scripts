from numpy import mean, std
from os import environ, system
from time import time

cmake_times = []
make_core_times = []
make_mesh_times = []
test_mesh_times = []

num_cores = '-j3'
num_runs = 1

for i in range(num_runs):

    # Reset environment
    environ['CC'] = ""
    environ['CXX'] = ""
    environ['PETSC_DIR'] = ""
    environ['PETSC_ARCH'] = ""

    # Reset build directory
    system('rm CMakeCache.txt')
    system('make clean')

    # Time configuration
    start = time()
    system('cmake ..')
    cmake_times.append(time() - start)

    # Time building libraries
    start = time()
    system('make %s chaste_core' % num_cores)
    make_core_times.append(time() - start)

    # Time building tests
    start = time()
    system('make %s mesh' % num_cores)
    make_mesh_times.append(time() - start)

    # Time running tests
    start = time()
    system('ctest %s -L mesh -E Parallel' % num_cores)
    test_mesh_times.append(time() - start)


with open('times.csv', 'w') as f:
    f.write(',mean,std\n')
    f.write('configure,%s,%s\n' % (mean(cmake_times), std(cmake_times)))
    f.write('build_libs,%s,%s\n' % (mean(make_core_times), std(make_core_times)))
    f.write('build_tests,%s,%s\n' % (mean(make_mesh_times), std(make_mesh_times)))
    f.write('run_tests,%s,%s\n' % (mean(test_mesh_times), std(test_mesh_times)))
