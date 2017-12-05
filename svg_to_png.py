import multiprocessing
import os
import subprocess

try:
    subprocess.call(['cairosvg', '--version'], stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
except OSError as e:
    raise ImportError('svg_to_png: cairosvg does not seem to be installed: ' + str(e))


def svg_to_png(path):
    """
    Given `path`, convert every svg file beneath it to a png, using `cairosvg`, in such a way as to consecutively
    name each png within each directory
    :param path: the path beneath which to search for svg files
    """

    # Get a unique list of directories containing svg files
    svg_dirs = get_set_of_svg_directories(path)

    # Get the list of commands
    command_list = get_list_of_commands(svg_dirs)

    print('svg_to_png: converting %s svg files using %s processes' % (len(command_list), multiprocessing.cpu_count()))

    # Execute the processes
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    pool.map_async(execute_command, command_list).get(86400)

    # Archive the svg files in each directory
    archive_svg_files(svg_dirs)


def get_set_of_svg_directories(path):
    """
    Determine the set of all directories under `path` containing svg files, or archives which will be extracted
    :param path: the path under which to search
    :return: a set of paths under `path` each of which contains at least one svg file
    """
    if not os.path.isdir(path):
        quit('Py: %s is not a valid directory' % path)

    svg_directories = set()

    archives = []

    for root, _, file_names in os.walk(path):
        for file_name in file_names:
            if file_name.endswith('.svg'):
                svg_directories.add(root)
            elif file_name == 'svg_arch.tar.gz':
                archives.append(root)

    # Extract any archives in-place
    for archive in archives:
        subprocess.call(['tar', '-zxf', 'svg_arch.tar.gz', '--overwrite'], cwd=archive)
        svg_directories.add(archive)

    return svg_directories


def get_list_of_commands(svg_dirs):
    """
    Get a list of commands for converting each svg to png using cairosvg
    :param svg_dirs: the list of directories containing svg files
    :return: a list of commands
    """
    command_list = []

    # Each directory must be processed separately so that PNGs can be sequentially named from 0
    for svg_dir in svg_dirs:
        svg_files = get_sorted_list_of_svg_in_dir(svg_dir)

        for idx, file_name in enumerate(svg_files):
            svg_name = os.path.join(svg_dir, file_name)
            png_name = os.path.join(svg_dir, str(idx).zfill(4) + '.png')
            command_list.append('cairosvg %s -o %s' % (svg_name, png_name))

    return command_list


def get_sorted_list_of_svg_in_dir(svg_dir):
    """
    Calculated an alphabetically-sorted list of svg files in a given directory
    :param svg_dir: the directory in which to look for svg files
    :return: a sorted list of svg files
    """
    if not os.path.isdir(svg_dir):
        quit('Py: %s is not a valid directory' % svg_dir)

    list_of_files = os.listdir(svg_dir)

    list_of_svg = []
    for file_name in list_of_files:
        if file_name.endswith('.svg'):
            # Verify the svg file is valid by finding the closing xml tag
            with open(os.path.join(svg_dir, file_name), 'r') as svg_file:
                if '</svg>' in svg_file.read():
                    list_of_svg.append(file_name)

    return sorted(list_of_svg)


def execute_command(cmd):
    """ Helper function to execute a single command in a multiprocessing Pool """
    return subprocess.call(cmd, shell=True)


def archive_svg_files(svg_dirs):
    """
    Archive svg files within each svg directory
    :param svg_dirs: the list of directories containing svg files
    """

    # Max compression
    os.environ['GZIP'] = '-9'

    for svg_dir in svg_dirs:
        svg_files = get_sorted_list_of_svg_in_dir(svg_dir)
        subprocess.call(['tar', '-zcf', 'svg_arch.tar.gz', '--remove-files'] + svg_files, cwd=svg_dir)


if __name__ == '__main__':
    quit('Call svg_to_png.svg_to_png()')
