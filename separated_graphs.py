import os
import shutil
import sys
from conans.test.utils.tools import NO_SETTINGS_PACKAGE_ID, TestClient

me = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    # Configure a test client to play with
    current_folder = os.path.join(me, '_working_dir')
    shutil.rmtree(current_folder)

    t = TestClient(path_with_spaces=False, current_folder=current_folder)
    t.run("config set general.default_package_id_mode=recipe_revision_mode")
    t.run("config set general.revisions_enabled=1")

    # Populate the cache
    t.run(f"export {me}/recipes/pyreq.py pyreq/0.1@")
    t.run(f"create {me}/recipes/ogg.py ogg/1.0@")
    t.run(f"create {me}/recipes/flac.py flac/1.0@")
    t.run(f"create {me}/recipes/vorbis.py vorbis/1.0@")

    t.run(f"lock create --reference flac/1.0@ --lockfile-out=flac_1.0.lock")
    t.run(f"lock create --reference vorbis/1.0@ --lockfile-out=vorbis_1.0.lock")

    t.save({'conanfile.txt': "[requires]\nflac/1.0\nvorbis/1.0\n"})
    t.run(f"lock create conanfile.txt --lockfile=flac_1.0.lock --lockfile=vorbis_1.0.lock --lockfile-out=project.lock")
