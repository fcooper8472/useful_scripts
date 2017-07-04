import os
import subprocess

# First, check that ffmpeg is installed
try:
    subprocess.call(['ffmpeg', '-version'], stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
except OSError as e:
    raise ImportError('png_to_mp4: ffmpeg does not seem to be installed: ' + str(e))


def png_to_mp4(sim_dir, mp4_name='results.mp4', mp4_duration=15.0, print_progress=False):
    """ Convert a sequence of png files to a mp4 movie

    :param sim_dir: the directory containing the simulation output
    :param mp4_name: file name for the mp4 (default 'results.mp4')
    :param mp4_duration: required duration in seconds for the mp4 (default 15.0)
    :param print_progress: whether to print running trace of this function (default False)

    :raise Exception: if sim_dir is not a valid directory
    :raise Exception: if mp4_duration is < 1.0
    :raise Exception: if no png files found in sim_dir
    :raise Exception: if ffmpeg does not generate mp4 file
    :raise Exception: if ffmpeg does not generate valid mp4 file (at least 1kb in size)
    """
    # Validate and process input
    if not (os.path.isdir(sim_dir)):
        raise Exception('png_to_mp4: Invalid simulation directory: ' + sim_dir)

    if not mp4_name.endswith('.mp4'):
        mp4_name += '.mp4'

    if mp4_duration < 1.0:
        raise Exception('png_to_mp4: Invalid mp4_duration: ' + str(mp4_duration))

    png_files = list_files_of_type(path_name=sim_dir, extension='.png')

    # "New" behaviour is to pre-convert the png files, so they should already exist
    if len(png_files) == 0:
        raise Exception('png_to_mp4: No png files found in ' + sim_dir)

    # Set how long you want the video to be (in seconds), and set the frame rate accordingly, with a minimum of 1.0
    frame_rate = max(float(len(png_files)) / mp4_duration, 1.0)

    # Send the subprocess call to run ffmpeg. Parameters:
    #   -v 0               Suppress console output so as not to clutter the terminal
    #   -r frame_rate      Set the frame rate calculated above
    #   -f image2          Set the convert format (image sequence to video)
    #   -i %04d.png        Input expected as dir/results.####.png, the output from WriteAnimation above
    #   -c:v libx264       Video codec to use is h264
    #   -crf 0             Set video quality to lossless
    #   -preset slow       Slow encoding at expense of slightly larger file size
    #   -y name.mp4        Output directory and name
    ffmpeg_command = ['ffmpeg',
                      '-v', '0',
                      '-r', str(frame_rate),
                      '-f', 'image2',
                      '-i', '%04d.png',
                      '-c:v', 'libx264',
                      '-crf', '0',
                      '-preset', 'slow',
                      '-y', mp4_name]

    if print_progress:
        print('png_to_mp4: Creating mp4: ' + ' '.join(ffmpeg_command))

    subprocess.call(ffmpeg_command, cwd=sim_dir, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))

    # Raise exception if the mp4 file is not generated as expected
    if not os.path.isfile(os.path.join(sim_dir, mp4_name)):
        raise Exception('png_to_mp4: mp4 not generated as expected')

    # Raise exception if the mp4 file file is created but is smaller than 1kb - ffmpeg sometimes
    # generates an empty file even if an error occurs
    if os.path.getsize(os.path.join(sim_dir, mp4_name)) < 1024:
        raise Exception('png_to_mp4: mp4 not generated as expected')

    if print_progress:
        print('\t... finished creating mp4: ' + mp4_name)

    # Tidy up: Delete all png files
    subprocess.call(['rm'] + png_files, cwd=sim_dir)
    if print_progress:
        print('png_to_mp4: Removed png files')

    # Tidy up: compress any vtu and pvd files, if they exist
    vtu_files = list_files_of_type(sim_dir, '.vtu') + list_files_of_type(sim_dir, '.pvd')
    if len(vtu_files) > 0:
        subprocess.call(['tar', '-zcf', 'vtu_arch.tar.gz', '--remove-files'] + vtu_files, cwd=sim_dir)
        if print_progress:
            print('png_to_mp4: Archived vtu and pvd files')

    # Tidy up: compress any other results files, if they exist
    res_files = []
    for res_file in os.listdir(sim_dir):
        if not (res_file.endswith('.mp4') or res_file.endswith('.tar.gz') or res_file.startswith('.')):
            res_files.append(res_file)

    if len(res_files) > 0:
        subprocess.call(['tar', '-zcf', 'res_arch.tar.gz', '--remove-files'] + res_files, cwd=sim_dir)
        if print_progress:
            print('png_to_mp4: Archived other results files')

    # Reset terminal
    os.system('stty sane')


def list_files_of_type(path_name, extension):
    """ Return a sorted list of files in a directory, with a specific extension

    :param path_name: the path to search in
    :param extension: the file extension to search for
    :return: a sorted list of all files in path_name with extension
    """
    if not extension.startswith('.'):
        extension = '.' + extension

    found_files = []
    for potential in os.listdir(path_name):
        if potential.endswith(extension):
            found_files.append(potential)
    return sorted(found_files)


if __name__ == '__main__':
    quit('Call png_to_mp4.png_to_mp4()')
