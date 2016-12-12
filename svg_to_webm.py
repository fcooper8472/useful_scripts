import os
import re
import subprocess

# First, check that inkscape and ffmpeg are installed
try:
    subprocess.call(['ffmpeg', '-version'], stdout=open(os.devnull, 'w'))
except OSError as e:
    raise ImportError('svg_to_webm: ffmpeg does not seem to be installed: ' + str(e))
try:
    subprocess.call(['inkscape', '-V'], stdout=open(os.devnull, 'w'))
except OSError as e:
    raise ImportError('svg_to_webm: inkscape does not seem to be installed: ' + str(e))


def svg_to_webm(sim_dir, webm_name='results.webm', webm_aspect_ratio=1.0, webm_duration=15.0, print_progress=False):
    """ Convert a sequence of svg files to a webm movie via a sequence of png files

    :param sim_dir: the directory containing the simulation output
    :param webm_name: file name for the webm (default 'results.webm')
    :param webm_aspect_ratio: required aspect ratio for the webm (default 1.0)
    :param webm_duration: required duration in seconds for the webm (default 15.0)
    :param print_progress: whether to print running trace of this function (default False)
    :return: nothing

    :raise Exception: if sim_dir is not a valid directory
    :raise Exception: if webm_aspect_ratio is < 1.0
    :raise Exception: if webm_duration is < 1.0
    :raise Exception: if no svg files found in sim_dir
    :raise Exception: if ffmpeg does not generate webm file
    :raise Exception: if ffmpeg does not generate valid webm file (at least 1kb in size)
    """
    # Validate and process input
    if not (os.path.isdir(sim_dir)):
        raise Exception('svg_to_webm: Invalid simulation directory: ' + sim_dir)

    if not webm_name.endswith('.webm'):
        webm_name += '.webm'

    if webm_aspect_ratio < 1.0:
        raise Exception('svg_to_webm: Invalid webm_aspect_ratio: ' + str(webm_aspect_ratio))

    if webm_duration < 1.0:
        raise Exception('svg_to_webm: Invalid webm_duration: ' + str(webm_duration))

    # Set GZIP environment variable to give max compression in tar stages
    os.environ['GZIP'] = '-9'

    # Check whether an svg archive exists.  If it does, extract it.  Then, list all svg files in the directory
    svg_archive_exists = 'svg_arch.tar.gz' in os.listdir(sim_dir)

    if svg_archive_exists:
        subprocess.call(['tar', '-zxf', 'svg_arch.tar.gz', '--overwrite'], cwd=sim_dir)
        if print_progress:
            print('svg_to_webm: Extracting svg files from archive svg_arch.tar.gz')

    svg_files = list_files_of_type(path_name=sim_dir, extension='.svg')

    # If there aren't any svg files at this point, something has gone wrong
    if len(svg_files) == 0:
        raise Exception('svg_to_webm: No svg files found in ' + sim_dir)

    # Use the first svg file to calculate information necessary to convert and crop the svg to png
    file_info = calculate_image_info(svg_file_path=os.path.join(sim_dir, svg_files[0]), aspect_ratio=webm_aspect_ratio)
    if print_progress:
        print('svg_to_webm: Calculated file information: ' + str(file_info))

    # Convert each svg to png
    if print_progress:
        print('svg_to_webm: Converting svg to png...')
    for idx, svg_file in enumerate(svg_files):
        svg_to_png(path_to_files=sim_dir, file_name=svg_file, file_info=file_info, index=idx)
        if print_progress:
            print('\t' + str(idx + 1) + ' of ' + str(len(svg_files)))
    if print_progress:
        print('\t... finished converting svg to png.')

    # Tidy up: Remove svg files, adding them to an archive if they are not already archived
    if svg_archive_exists:
        subprocess.call(['rm'] + svg_files, cwd=sim_dir)
        if print_progress:
            print('svg_to_webm: Removed svg files')
    else:
        subprocess.call(['tar', '-zcf', 'svg_arch.tar.gz', '--remove-files'] + svg_files, cwd=sim_dir)
        if print_progress:
            print('svg_to_webm: Archived svg files to svg_arch.tar.gz')

    # Set how long you want the video to be (in seconds), and set the frame rate accordingly
    png_files = list_files_of_type(path_name=sim_dir, extension='.png')
    frame_rate = float(len(png_files)) / webm_duration

    # Send the subprocess call to run ffmpeg. Parameters:
    #   -v 0               Suppress console output so as not to clutter the terminal
    #   -r frame_rate      Set the frame rate calculated above
    #   -f image2          Set the convert format (image sequence to video)
    #   -i %04d.png        Input expected as dir/results.####.png, the output from WriteAnimation above
    #   -c:v libvpx-vp9    Video codec to use is vp9
    #   -lossless', '1'    Set video quality to lossless
    #   -y name.webm       Output directory and name
    if print_progress:
        print('svg_to_webm: Creating webm: ' + webm_name)
    subprocess.call(['ffmpeg',
                     '-v', '0',
                     '-r', str(frame_rate),
                     '-f', 'image2',
                     '-i', '%04d.png',
                     '-c:v', 'libvpx-vp9',
                     '-lossless', '1',
                     '-y', webm_name], cwd=sim_dir)

    # Raise exception if the webm file is not generated as expected
    if not os.path.isfile(os.path.join(sim_dir, webm_name)):
        raise Exception('svg_to_webm: webm not generated as expected')

    # Raise exception if the webm file file is created but is smaller than 1kb - ffmpeg sometimes
    # generates an empty file even if an error occurs
    if os.path.getsize(os.path.join(sim_dir, webm_name)) < 1024:
        raise Exception('svg_to_webm: webm not generated as expected')

    if print_progress:
        print('\t... finished creating webm: ' + webm_name)

    # Tidy up: Delete all png files
    subprocess.call(['rm'] + png_files, cwd=sim_dir)
    if print_progress:
        print('svg_to_webm: Removed png files')

    # Tidy up: compress any vtu and pvd files, if they exist
    vtu_files = list_files_of_type(sim_dir, '.vtu') + list_files_of_type(sim_dir, '.pvd')
    if len(vtu_files) > 0:
        subprocess.call(['tar', '-zcf', 'vtu_arch.tar.gz', '--remove-files'] + vtu_files, cwd=sim_dir)
        if print_progress:
            print('svg_to_webm: Archived vtu and pvd files')

    # Tidy up: compress any other results files, if they exist
    res_files = []
    for res_file in os.listdir(sim_dir):
        if not (res_file.endswith('.webm') or res_file.endswith('.tar.gz') or res_file.startswith('.')):
            res_files.append(res_file)
    print(res_files)
    if len(res_files) > 0:
        subprocess.call(['tar', '-zcf', 'res_arch.tar.gz', '--remove-files'] + res_files, cwd=sim_dir)
        if print_progress:
            print('svg_to_webm: Archived other results files')


# Helper function for svg_to_webm: list all files with a particular extension in the simulation directory
def list_files_of_type(path_name, extension):

    if not extension.startswith('.'):
        extension = '.' + extension

    found_files = []
    for potential in os.listdir(path_name):
        if potential.endswith(extension):
            found_files.append(potential)
    return sorted(found_files)


# Helper function for svg_to_webm: interrogate an svg file to calculate global values of interest
def calculate_image_info(svg_file_path, aspect_ratio):

    # First get the dimensions of the svg file. We use a regex pattern to look for the vieBox attribute
    regex_pattern = 'viewBox="0 0 (\d*\.?\d* \d*\.?\d*)".*?'
    dimension_strings = re.findall(regex_pattern, open(svg_file_path).read())

    if len(dimension_strings) != 1:
        raise Exception('svg_to_webm: Did not successfully extract svg dimensions from ' + svg_file_path)

    # Convert the dimension string to two floats, and validate
    dimensions = [float(s) for s in dimension_strings[0].split()]
    if len(dimensions) != 2:
        raise Exception('svg_to_webm: Did not successfully extract svg dimensions from ' + svg_file_path)

    file_info = {'svg_width': dimensions[0],
                      'svg_height': dimensions[1],
                      'png_width': int(dimensions[0]),
                      'png_height': int(dimensions[0] / aspect_ratio),
                      'png_y_offset': int(0.5 * (dimensions[1] - dimensions[1] / aspect_ratio))}

    file_info['crop_string'] = '{0}:{1}:{2}:{3}'.format(str(0),
                                                        str(file_info['png_y_offset']),
                                                        str(file_info['png_width']),
                                                        str(file_info['png_y_offset'] + file_info['png_height']))

    return file_info


def svg_to_png(path_to_files, file_name, file_info, index):
    FNULL = open(os.devnull, 'w')
    subprocess.call(['inkscape', '-z',
                     '-e', str(index).zfill(4) + '.png',
                     '-a', file_info['crop_string'],
                     file_name], cwd=path_to_files, stdout=FNULL)

if __name__ == '__main__':
    svg_to_webm('/scratch/fcooper/chaste_test_output/TestShortMultiCellSimulation/results_from_time_0', 'test_movie', 16.0/9)
