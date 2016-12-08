import os
# import platform


def svg_to_webm(sim_dir, webm_name='movie'):

    # Validate data directory
    if not (os.path.isdir(sim_dir)):
        raise Exception('svg_to_webm: Invalid simulation directory')

    svg_files = list_all_svg(path_name=sim_dir)

    if len(svg_files) == 0:
        raise Exception('svg_to_webm: No svg files found in ' + sim_dir)


# Helper function for svg_to_webm: list all svg files in the simulation directory
def list_all_svg(path_name):

    svg_files = []
    for potential_svg in os.listdir(path_name):
        if potential_svg.endswith('.svg'):
            svg_files.append(potential_svg)
    return svg_files

def svg_to_png(path_name, list_of_files):


if __name__ == '__main__':
    svg_to_webm('/scratch/chaste_test_output/TestShortMultiCellSimulation/results_from_time_0', 'test_movie')
