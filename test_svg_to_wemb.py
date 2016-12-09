import svg_to_webm

sim_dir = '/scratch/Cooper/chaste_test_output/TestShortMultiCellSimulation/results_from_time_0'

try:
    svg_to_webm.svg_to_webm(sim_dir=sim_dir, webm_name='result', webm_aspect_ratio=16.0 / 9, webm_duration=12.0)
except Exception as e:
    print "Exception: " + str(e)
