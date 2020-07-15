from conans import ConanFile

class Recipe(ConanFile):
    name = "pyreq"
    version = "0.1"


class BaseMixin:
    def configure(self):
        self.output.info(f"{self.name}/{self.version}: configure()")
