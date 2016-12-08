import os
import re
import subprocess
import platform


def svg_to_webm(sim_dir, webm_name='results.webm', webm_aspect_ratio=1.0):

    # Validate data directory
    if not (os.path.isdir(sim_dir)):
        raise Exception('svg_to_webm: Invalid simulation directory')

    if not webm_name.endswith('.webm'):
        webm_name += '.webm'

    # Check whether an svg archive exists.  If it does, extract it.  Then, list all svg files in the directory
    svg_archive_exists = 'svg_arch.tar.gz' in os.listdir(sim_dir)

    if svg_archive_exists:
        subprocess.call(['tar', '-zxf', 'svg_arch.tar.gz', '--overwrite'], cwd=sim_dir)

    svg_files = list_files_of_type(path_name=sim_dir, extension='.svg')

    # If there aren't any svg files at this point, something has gone wrong
    if len(svg_files) == 0:
        raise Exception('svg_to_webm: No svg files found in ' + sim_dir)

    # Use the first svg file to calculate information necessary to convert and crop the svg to png
    file_info = calculate_image_info(svg_file_path=os.path.join(sim_dir, svg_files[0]), aspect_ratio=webm_aspect_ratio)

    # Convert each svg to png
    for idx, svg_file in enumerate(svg_files):
        svg_to_png(path_to_files=sim_dir, file_name=svg_file, file_info=file_info, index=idx)
        print('Converted svg ' + str(idx) + ' of ' + str(len(svg_files)))

    png_files = list_files_of_type(path_name=sim_dir, extension='.png')
    print(png_files)

    # Set how long you want the video to be (in seconds), and set the frame rate accordingly
    video_duration = 15.0
    frame_rate = str(float(len(png_files)) / video_duration)

    # Send the system command to run avconv/ffmpeg. Parameters:
    #   -v 0                        Suppress console output so as not to clutter the terminal
    #   -r frame_rate               Set the frame rate calculated above
    #   -f image2                   Set the convert format (image sequence to video)
    #   -i dir/results.%04d.png     Input expected as dir/results.####.png, the output from WriteAnimation above
    #   -c:v h264                   Video codec to use is h264
    #   -crf 0                      Set video quality: 0 best, 51 worst (https://trac.ffmpeg.org/wiki/Encode/H.264)
    #   -y dir/movie.mp4            Output directory and name
    subprocess.call(['ffmpeg',
                     '-v', '0',
                     '-r', str(frame_rate),
                     '-f', 'image2',
                     '-i', '%04d.png',
                     '-c:v', 'libvpx-vp9',
                     '-lossless', '1',
                     '-y', webm_name], cwd=sim_dir)

    # # Raise exception if the mp4 file is not generated as expected
    # if not (os.path.isfile(full_movie_path)):
    #     raise Exception('pvd_to_mp4: mp4 not generated as expected')
    #
    # # Raise exception if the mp4 file file is created but is smaller than 1kb - ffmpeg sometimes
    # # generates an empty file even if an error occurs
    # if os.path.getsize(full_movie_path) < 1024:
    #     raise Exception('pvd_to_mp4: mp4 not generated as expected')










    # Remove svg files, adding them to an archive if they are not already archived
    if svg_archive_exists:
        subprocess.call(['rm'] + svg_files, cwd=sim_dir)
    else:
        subprocess.call(['tar', '-zcf', 'svg_arch.tar.gz', '--remove-files'] + svg_files, cwd=sim_dir)

    # Delete all png files
    subprocess.call(['rm'] + png_files, cwd=sim_dir)


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

    file_info_dict = {'svg_width': dimensions[0],
                      'svg_height': dimensions[1],
                      'png_width': int(dimensions[0]),
                      'png_height': int(dimensions[0] / aspect_ratio),
                      'png_y_offset': int(0.5 * (dimensions[1] - dimensions[1] / aspect_ratio))}

    file_info_dict['crop_string'] = '{0}x{1}+0+{2}'.format(str(file_info_dict['png_width']),
                                                           str(file_info_dict['png_height']),
                                                           str(file_info_dict['png_y_offset']))

    return file_info_dict


def svg_to_png(path_to_files, file_name, file_info, index):
    subprocess.call(['convert', os.path.join(path_to_files, file_name),
                     '-crop', file_info['crop_string'],
                     os.path.join(path_to_files, str(index).zfill(4) + '.png')])

if __name__ == '__main__':
    svg_to_webm('/scratch/fcooper/chaste_test_output/TestShortMultiCellSimulation/results_from_time_0', 'test_movie', 16.0/9)
