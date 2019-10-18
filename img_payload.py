from imghdr import what

from PIL import Image

from injectors import *
from argparse import ArgumentParser
from logger import *
from os.path import basename, join, exists, isdir
from os import mkdir, listdir, devnull, remove
from shutil import move, copy, rmtree
from subprocess import call
from shlex import split
from time import time
from pathlib import Path

_HEADER = Fore.BLUE + """
 _                           _           _ 
|_|_____ ___ ___ ___ ___ _ _| |___ ___ _| |
| |     | . |___| . | .'| | | | . | .'| . |
|_|_|_|_|_  |   |  _|__,|_  |_|___|__,|___|
        |___|   |_|     |___|              
""" + Style.RESET_ALL + Fore.WHITE + """
 Inject payloads into image files
""" + Style.RESET_ALL

temp_dir = "tmp"
results_dir = "results"

prefix_temp_img = "tmp_"

image_file_variable = "{img}"
out_image_file_variable = "{outimg}"

print(_HEADER)

parser = ArgumentParser()
parser.add_argument("payload", type=str, help="The payload to be injected into the image file")
parser.add_argument("images", nargs="+", type=str,
                    help="The image files where the payload gets injected")
parser.add_argument("--beat", type=str, required=False, metavar="BEAT",
                    help="Shell command that shall be beaten (f.E. convert, php, ...)")

args = parser.parse_args()

source_image_files = args.images
payload = args.payload
beat_cmd = args.beat

successes = 0


def is_image(file):
    try:
        Image.open(file)
        return True
    except:
        return False
    return True


def create_temp_image(base_img_file):
    temp_name = join(temp_dir, "%s%s" % (prefix_temp_img, basename(base_img_file)))
    if exists(temp_name):
        rm_file(temp_name)
    open(temp_name, "wb").write(open(base_img_file, "rb").read())
    return temp_name


def move_successful_image(image_file, injector, injection_info):
    new_name = basename(image_file).replace(prefix_temp_img, "") + "_" + injection_info.file_ending + Path(
        image_file).suffix
    move(image_file, join(results_dir, new_name))


def copy_images():
    info("Copying images ...")
    for image_file in source_image_files:
        new_name = join(temp_dir, basename(image_file))
        copy(image_file, new_name)


def test_image(temp_img_file):
    if len(beat_cmd) > 0:
        fnull = open(devnull, "w")
        cmd_args = split(beat_cmd.replace(image_file_variable, temp_img_file).replace(out_image_file_variable,
                                                                                      temp_img_file + "_out"))
        if call(cmd_args, shell=False, stdout=fnull, stderr=fnull) != 0:
            return False
    check_file = temp_img_file

    if exists(temp_img_file + "_out"):
        check_file = temp_img_file + "_out"

    data = open(check_file, "rb").read()

    return payload in data and is_image(temp_img_file)


def rm_file(file):
    if not exists(file):
        return

    if is_dir(file):
        rmtree(file)
    else:
        remove(file)


def is_dir(file):
    return exists(file) and isdir(file)


def main():
    rm_file(temp_dir)
    rm_file(results_dir)

    mkdir(temp_dir)
    mkdir(results_dir)

    copy_images()

    image_files = [join(temp_dir, x) for x in listdir(temp_dir)]

    info("Payload: %s" % payload)
    info("Command to beat: %s" % str(beat_cmd))
    info("Images (%d): %s" % (len(image_files), ", ".join(image_files)))

    total_successes = 0

    for image_file in image_files:
        print("")
        info("Processing image '%s'" % image_file)

        injectors = [CommentInjector(), BinaryDataInjector()]

        try_index = 0

        for injector in injectors:
            start_time = time()
            last_time = start_time

            successes = 0
            curr_iter = 0
            iterations = injector.estimate_iterations(image_file, payload)
            info("Running " + injector.get_name() + " module")
            while not injector.is_done(image_file):
                temp_img_file = create_temp_image(image_file)
                injection_info = injector.try_next(temp_img_file, payload)

                if try_index % 50 == 0:
                    if time() - last_time > 15:
                        last_time = time()
                        remaining = ((last_time - start_time) / float(curr_iter)) * (iterations - curr_iter)
                        percent = (float(curr_iter) / float(iterations)) * 100
                        info("Progress: %d" % percent + "%" + " (%d/%d), about %ds remaining" % (
                            curr_iter, iterations, remaining))

                if test_image(temp_img_file):
                    successes += 1
                    move_successful_image(temp_img_file, injector, injection_info)
                    info_success("Injection in file '%s' in module '%s', %s" % (
                        basename(temp_img_file), injector.get_name(), injection_info.message))
                try_index += 1
                curr_iter += 1
            if successes > 0:
                info_success("Module '%s' found %d injection point(s), saved to results directory" % (
                    injector.get_name(), successes))
            else:
                warning("Module '%s' found no injection points." % injector.get_name())

            total_successes += successes

    print("")
    if total_successes > 0:
        info_success(
            "%d injection points were found that survived the given command. They can be found in "
            "the '%s' directory." % (total_successes, results_dir))
    else:
        info_failure("No injection points for the payload were found in the images.")

    rm_file(temp_dir)


if __name__ == "__main__":
    main()
