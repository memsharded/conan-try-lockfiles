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

    # Create graphs for different branches
    t.run(f"lock create --reference flac/1.0@ --lockfile-out=flac_1.0.lock")
    t.run(f"lock create --reference vorbis/1.0@ --lockfile-out=vorbis_1.0.lock")

    # Use two lockfiles to build a consumer one
    t.save({'conanfile.txt': "[requires]\nflac/1.0\nvorbis/1.0\n"})
    t.run(f"lock create conanfile.txt --lockfile=flac_1.0.lock --lockfile=vorbis_1.0.lock --lockfile-out=project.lock", assert_error=True)
    # TODO: Merge input lockfiles first and then run as usual.
    #   - approach#1: New cache, install both lockfiles and create the new one:
    #       ```
    #       conan install flac_1.0.lock 
    #       conan install vorbis_1.0.lock 
    #       conan lock create conanfile.txt --lockfile-out=project.lock
    #       ```
    #       Approach invalid, it doesn't raise for inconsistencies between lockfiles
    #
    #   - approach#2: Merge the two lockfiles as JSON
    #       Do not store the profile in the lockfile, but store settings and options per node. Merging
    #       two lockfiles would be as easy as adding two JSONs (raise if two nodes with the same key
    #       contain different information).
    #
    #       Prerequisite.- Key for nodes is '<context>::<ref-name>' instead of a random number

