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

    # Create the lockfiles injecting CMake dynamically
    t.run(f"lock create --reference=flac/1.0@ --lockfile-out=flac.lock --profile=../profiles/host_with_cmake --build=flac")
