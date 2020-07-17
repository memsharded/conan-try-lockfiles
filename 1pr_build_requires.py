import os
import shutil
import sys
from conans.test.utils.tools import TestClient
from conans import tools

me = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")


if __name__ == '__main__':
    # Configure a test client to play with
    working_dir = os.path.join(me, '_working_dir')
    shutil.rmtree(working_dir, ignore_errors=True)

    t = TestClient(path_with_spaces=False, current_folder=working_dir)
    t.run("config set general.default_package_id_mode=recipe_revision_mode")
    t.run("config set general.revisions_enabled=1")

    # Populate the cache
    t.run(f"export {me}/recipes/pyreq.py pyreq/0.1@")
    t.run(f"create {me}/recipes/ogg.py ogg/1.0@")
    t.run(f"create {me}/recipes/cmake.py cmake/1.0@")
    t.run(f"create {me}/recipes/flac.py flac/1.0@")
    t.run(f"create {me}/recipes/consumer_flac.py consumer_flac/1.0@")

    # Create the lockfile: do not lock the build_requires
    t.run(f"lock create --reference=consumer_flac/1.0@ --lockfile-out=consumer_flac.lock")
    t.run(f"install consumer_flac/1.0@ --lockfile=consumer_flac.lock")
    t.run(f"create {me}/recipes/consumer_flac.py consumer_flac/1.0@ --lockfile=consumer_flac.lock", assert_error=True)
    # TODO: I cannot use the lockfile to build the package because the 'cmake' is not in the lockfile

    # Create the lockfile with the build_requires
    t.run(f"lock create --reference=consumer_flac/1.0@ --lockfile-out=consumer_flac.lock --build")
    t.run(f"install consumer_flac/1.0@ --lockfile=consumer_flac.lock --lockfile-out=consumer_flac.install.out.lock")
    assert 'cmake' not in t.out
    # assert 'cmake' not in tools.load(os.path.join(me, working_dir, "consumer_flac.install.out.lock")), "CMake in the lockfile!"
    # TODO: the 'cmake' node was never used and it is in the output!!!

    t.run(f"create {me}/recipes/consumer_flac.py consumer_flac/1.0@ --lockfile=consumer_flac.lock --lockfile-out=consumer_flac.create.out.lock")
    # TODO: I understand CMake in the output, it is more information, but if I upgrade my dev tools, this means that the output
    #   lockfile will no longer be usable.
    