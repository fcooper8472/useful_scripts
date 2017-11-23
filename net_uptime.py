import atexit
import datetime
import subprocess

from collections import deque
from time import sleep

g_start_time = datetime.datetime.now()
g_time_format = '%Y-%m-%d %H:%M:%S'
g_num_failures_before_log = 3
g_sleep_time = 1.0
g_failures = deque([False] * g_num_failures_before_log, g_num_failures_before_log)
g_log_name = '/home/fergus/net_uptime_log'
g_cumulative_failure_duration = g_start_time - g_start_time
g_num_failures = 0
g_currently_in_failure = False
g_failure_start_time = datetime.datetime.now()


def exit_handler():
    end_time = datetime.datetime.now()
    total_duration = (end_time - g_start_time).seconds
    failure_duration = g_cumulative_failure_duration.seconds
    if total_duration > 0:
        proportion = 100.0 * failure_duration / total_duration
    else:
        proportion = 0.0
    log('%s Ending log after %s with %s failures (%ss, %s%%)\n################################\n' %
        (end_time.strftime(g_time_format), format_seconds(total_duration), g_num_failures, failure_duration, proportion))
atexit.register(exit_handler)


def format_seconds(seconds):
    if seconds < 60:
        return '%ss' % seconds
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return '%sm %ss' % (m, s)
    else:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return '%sh %sm %ss' % (h, m, s)


def log(message):
    with open(g_log_name, "a") as myfile:
        myfile.write(message)


def main():

    global g_currently_in_failure
    global g_failure_start_time
    global g_num_failures
    global g_cumulative_failure_duration

    a = subprocess.Popen(['ping', '-c', '3', '-i', '0.2', '8.8.8.8'], stdout=subprocess.PIPE)

    output, _ = a.communicate()

    if "received, 0% packet loss" not in output:
        g_failures.append(True)
    elif g_currently_in_failure:
        g_currently_in_failure = False
        now = datetime.datetime.now()
        failure_duration = now - g_failure_start_time
        g_cumulative_failure_duration += failure_duration
        log('%s Failure end (duration %ss)\n' % (now.strftime(g_time_format), failure_duration.seconds))

    if g_failures.count(False) == 0 and not g_currently_in_failure:
        g_currently_in_failure = True
        now = datetime.datetime.now()
        g_failure_start_time = now
        g_num_failures += 1
        log('%s Failure start\n' % now.strftime(g_time_format))


if __name__ == '__main__':

    log('\n################################\n%s Starting log\n' % g_start_time.strftime(g_time_format))

    while True:
        main()
        sleep(g_sleep_time)

