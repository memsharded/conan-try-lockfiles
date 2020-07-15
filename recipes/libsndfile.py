from conans import ConanFile
from conans import tools
from conans.errors import ConanInvalidConfiguration

class Recipe(ConanFile):
    name = "libsndfile"
    #version = "1.0.28"

    python_requires = "pyreq/0.1"
    python_requires_extend = "pyreq.BaseMixin"

    def requirements(self):
        self.requires("flac/[>=0.0]")
        self.requires("vorbis/[>=0.0]")

    def build(self):
        # Quite stupid, but this recipe only works with an odd version of `ogg`
        ogg_version = tools.Version(self.deps_cpp_info["ogg"].version)
        if int(ogg_version.major) % 2 == 0:
            raise ConanInvalidConfiguration(f"Detected even version of 'ogg' ({ogg_version}), not allowed")
