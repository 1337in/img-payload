from subprocess import call
from shlex import split


class InjectorResult:
    def __init__(self, message, file_ending):
        self.message = message
        self.file_ending = file_ending


class Injector:

    def try_next(self, image_file, payload):
        pass

    def is_done(self, image_file):
        pass

    def get_name(self):
        return self.__class__.__name__.lower().replace("injector", "")

    def estimate_iterations(self, image_file, payload):
        return 0


class CommentInjector(Injector):

    def __init__(self):
        self.idx = -1
        pass

    def try_next(self, image_file, payload):
        self.idx += 1
        if self.idx == 0:
            #todo escape payload
            call(split("exiftool -comment='" + payload + "' " + image_file), shell=False)
            return InjectorResult("injected into image comment section", "comment")

    def is_done(self, image_file):
        return self.idx >= 0

    def estimate_iterations(self, image_file, payload):
        return 1


class BinaryDataInjector(Injector):

    def __init__(self):
        self.idx = 0

    def try_next(self, image_file, payload):
        data = open(image_file, "rb").read()
        new_dat = list(data)
        new_dat.insert(self.idx, payload)
        open(image_file, "wb").write("".join(new_dat))
        before_idx = self.idx
        self.idx += 1
        return InjectorResult("injected into binary data at offset %d" % before_idx, "binary_%d" % before_idx)

    def is_done(self, image_file):
        return self.idx >= len(open(image_file, "rb").read()) - 1

    def estimate_iterations(self, image_file, payload):
        return len(open(image_file, "rb").read())
