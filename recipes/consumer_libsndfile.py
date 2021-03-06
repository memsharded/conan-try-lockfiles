from conans import ConanFile

class Recipe(ConanFile):
    name = "consumer_libsndfile"

    python_requires = "pyreq/0.1"
    python_requires_extend = "pyreq.BaseMixin"

    def requirements(self):
        self.requires("libsndfile/[>=0.0]")
