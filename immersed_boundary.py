import os
import platform

try:
    import paraview.simple as pv
except ImportError:
    print("Py: ParaView module not imported - is ParaView in the python path?")


def pvd_to_mp4(sim_dir, path_to_movies, movie_name='movie', representation='Surface', num_regions=0):

    ###############################
    # Validate directory and data #
    ###############################

    if not (os.path.isdir(sim_dir)):
        raise Exception('pvd_to_mp4: Invalid simulation directory')

    if not (os.path.isdir(path_to_movies)):
        raise Exception('pvd_to_mp4: Invalid movie directory')

    if representation not in ['Surface', 'Points']:
        raise Exception('pvd_to_mp4: Representation must be either Surface or Points')

    if num_regions not in [0, 9]:
        raise Exception('pvd_to_mp4: Currently there is only support for 9 node regions')

    # sim_id = os.path.basename(os.path.normpath(sim_dir))

    possible_data_directories = []
    for directory in os.listdir(sim_dir):
        if directory.startswith('results_from_time'):
            possible_data_directories.append(os.path.join(sim_dir, directory))

    if len(possible_data_directories) == 0:
        raise Exception('pvd_to_mp4: Could not find a "results_from_time_X" directory')

    # The last directory alphabetically will be the one after any initial relaxation simulation
    data_directory = sorted(possible_data_directories)[-1]

    # Get the location of the pvd file
    pvd_file = os.path.join(data_directory, 'results.pvd')
    if not(os.path.isfile(pvd_file)):
        raise Exception('pvd_to_mp4: Could not find a pvd data file')

    if os.path.getsize(pvd_file) < 1024:
        raise Exception('pvd_to_mp4: pvd file exists but is < 1kb. Presumably simulation failed to finish as expected.')

    full_movie_path = os.path.join(path_to_movies, movie_name + '_' + representation + '.mp4')

    ##################################
    # Set up scene with box and data #
    ##################################

    # Get active view. This is the ParaView default view - blue background with cross hairs and orientation axes
    render_view = pv.GetActiveViewOrCreate('RenderView')

    # Change parameters to be how we want them for output
    render_view.ViewSize = [1600, 900]          # Size of output (pixels)
    render_view.CenterAxesVisibility = 0        # Remove cross hairs
    render_view.OrientationAxesVisibility = 0   # Remove orientation axes
    render_view.Background = [0.5, 0.5, 0.5]    # Set background colour to 50% grey

    # Create a unit square (a 3D Box with ZLength set to zero)
    unit_square = pv.Box()
    unit_square.ZLength = 0.0
    unit_square.YLength = 9.0 / 16.0
    unit_square.Center = [0.5, 0.5, 0.0]

    # Show the box in the current render view, and colour it black
    unit_square_display = pv.Show(unit_square, render_view)
    unit_square_display.DiffuseColor = [0.0, 0.0, 0.0]

    # Read the relevant pvd file from the Chaste output
    results_pvd = pv.PVDReader(FileName=pvd_file)

    # Show the data in the current render view as a surface
    results_pvd_display = pv.Show(results_pvd, render_view)
    results_pvd_display.Representation = representation

    if representation == 'Points' and num_regions == 9:
        pv.ColorBy(results_pvd_display, ('POINTS', 'Node Regions'))
        node_regions_lut = pv.GetColorTransferFunction('NodeRegions')

        # Each four digits are: data value, r, g, b (colour)
        node_regions_lut.RGBPoints = [0.0, 1.00, 0.00, 0.00,  # LEFT_APICAL_REGION, red
                                      1.0, 1.00, 0.00, 0.00,  # RIGHT_APICAL_REGION, red
                                      2.0, 1.00, 0.00, 1.00,  # LEFT_PERIAPICAL_REGION, purple
                                      3.0, 1.00, 0.00, 1.00,  # RIGHT_PERIAPICAL_REGION, purple
                                      4.0, 0.00, 0.00, 1.00,  # LEFT_LATERAL_REGION, blue
                                      5.0, 0.00, 0.00, 1.00,  # RIGHT_LATERAL_REGION, blue
                                      6.0, 1.00, 1.00, 1.00,  # LEFT_BASAL_REGION, white
                                      7.0, 1.00, 1.00, 1.00,  # RIGHT_BASAL_REGION, white
                                      8.0, 1.00, 1.00, 1.00]  # LAMINA_REGION, white

        cell_regions_lut = pv.GetColorTransferFunction('CellRegions')
        cell_regions_lut.RGBPoints = [-1.0, 0.0, 0.00, 0.00,  # basal lamina, black
                                      0.0, 0.00, 0.00, 1.00,  # left region, blue
                                      1.0, 1.00, 1.00, 1.00,  # centre_region, white
                                      2.0, 1.00, 0.00, 0.00]  # right_region, red

        # Glyphs for cell region
        cell_glyphs = pv.Glyph(Input=results_pvd, GlyphType='2D Glyph')

        cell_glyphs.Scalars = ['CELLS', 'Cell Regions']
        cell_glyphs.ScaleFactor = 0.01
        cell_glyphs.GlyphMode = 'All Points'
        cell_glyphs.GlyphType.GlyphType = 'Diamond'
        cell_glyphs.GlyphType.Filled = 1
        cell_glyphs.GlyphTransform.Scale = [1.0, 2.0, 1.0]

        cell_glyphs_display = pv.Show(cell_glyphs, render_view)
        cell_glyphs_display.Opacity = 0.5

        # Glyphs for node region
        node_glyphs = pv.Glyph(Input=results_pvd, GlyphType='2D Glyph')

        node_glyphs.Scalars = ['POINTS', 'Node Regions']
        node_glyphs.ScaleFactor = 0.002
        node_glyphs.GlyphMode = 'All Points'
        node_glyphs.GlyphType.GlyphType = 'Circle'
        node_glyphs.GlyphType.Filled = 1

        pv.Show(node_glyphs, render_view)

    ###################################
    # Put the camera where we want it #
    ###################################

    # This happens after all calls to Show, as Show may do some automatic camera re-setting
    render_view.InteractionMode = '2D'
    render_view.CameraPosition = [0.5, 0.5, 1.0]
    render_view.CameraFocalPoint = [0.5, 0.5, 0.0]

    # This parameter sets the 'zoom' and needs fine-tuning by the aspect ratio
    render_view.CameraParallelScale = 0.5 * 9.0 / 16.0

    ##################################
    # Set up and write the animation #
    ##################################

    # Get an animation scene, which has parameters we need to change before output
    animation_scene = pv.GetAnimationScene()

    # Get a list of time step values from the pvd file.  Typically this will look like [t_0, t1, t2, ..., t_end]
    time_step_info = results_pvd.TimestepValues
    num_time_steps = len(time_step_info)

    # Set the animation parameters
    animation_scene.NumberOfFrames = num_time_steps  # If num frames != num time steps, some interpolation will be used
    animation_scene.StartTime = time_step_info[0]    # Usually t_0, the first entry in time_step_info
    animation_scene.EndTime = time_step_info[-1]     # Usually t_end, the final entry in time_step_info

    # Write the animation as a series of uncompressed png files, with no magnification
    pv.WriteAnimation(sim_dir + 'results_' + representation + '.png', Magnification=1, Compression=False)

    # Raise exception if the png files are not generated as expected
    if not(os.path.isfile(sim_dir + 'results_' + representation + '.0000.png')):
        raise Exception('pvd_to_mp4: png sequence not exported as expected')

    #######################################
    # Convert from png to mp4 and tidy up #
    #######################################

    # Ubuntu 14.04 (trusty) came bundled with avconv instead of ffmpeg, but they're nearly the same software
    # so we don't have to change the command other than the name of the video converter to use
    if platform.linux_distribution()[2] == 'trusty':
        video_converter = 'avconv'
    else:
        video_converter = 'ffmpeg'

    # Set how long you want the video to be (in seconds), and set the frame rate accordingly
    video_duration = 15.0
    frame_rate = str(num_time_steps / video_duration)

    # Send the system command to run avconv/ffmpeg. Parameters:
    #   -v 0                        Suppress console output so as not to clutter the terminal
    #   -r frame_rate               Set the frame rate calculated above
    #   -f image2                   Set the convert format (image sequence to video)
    #   -i dir/results.%04d.png     Input expected as dir/results.####.png, the output from WriteAnimation above
    #   -c:v h264                   Video codec to use is h264
    #   -crf 0                      Set video quality: 0 best, 51 worst (https://trac.ffmpeg.org/wiki/Encode/H.264)
    #   -y dir/movie.mp4            Output directory and name
    os.system(video_converter + ' -v 0 -r ' + frame_rate + ' -f image2 -i ' + sim_dir +
              'results_' + representation + '.%04d.png -c:v h264 -crf 0 -y ' + full_movie_path)

    # Raise exception if the mp4 file is not generated as expected
    if not(os.path.isfile(full_movie_path)):
        raise Exception('pvd_to_mp4: mp4 not generated as expected')

    # Raise exception if the mp4 file file is created but is smaller than 1kb - ffmpeg sometimes
    # generates an empty file even if an error occurs
    if os.path.getsize(full_movie_path) < 1024:
        raise Exception('pvd_to_mp4: mp4 not generated as expected')

    # Clean up the png files created by WriteAnimation
    os.system('rm ' + sim_dir + '*.png')
