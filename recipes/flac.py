from conans import ConanFile

class Recipe(ConanFile):
    name = "flac"
    #version = "1.3.3"

    python_requires = "pyreq/0.1"
    python_requires_extend = "pyreq.BaseMixin"

    def requirements(self):
        self.requires("ogg/[>=0.0]")
