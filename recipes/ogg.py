from conans import ConanFile

class Recipe(ConanFile):
    name = "ogg"
    #version = "1.3.4"

    python_requires = "pyreq/0.1"
    python_requires_extend = "pyreq.BaseMixin"
