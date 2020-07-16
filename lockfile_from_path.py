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
    t.run(f"create {me}/recipes/libsndfile.py libsndfile/1.0@")

    # Using conanfile.txt
    t.run(f"lock create {me}/recipes/consumer.txt --lockfile-out=output.lock")
    t.run(f"install {me}/recipes/consumer.txt --lockfile=output.lock")

    # Using conanfile.py (without name and version)
    t.run(f"lock create {me}/recipes/consumer_noname.py --lockfile-out=output.lock")
    t.run(f"create {me}/recipes/consumer_noname.py consumer_libsndfile/1.0@ --lockfile=output.lock", assert_error=True)  # Mismatch name/version
    t.run(f"create {me}/recipes/consumer_noname.py  --lockfile=output.lock", assert_error=True)  # Cannot create without name/version
    t.run(f"install {me}/recipes/consumer_noname.py --lockfile=output.lock")

    # Using conanfile.py (with name and version)
    t.run(f"lock create {me}/recipes/consumer_noname.py --lockfile-out=output.lock --name=name --version=version")
    t.run(f"create {me}/recipes/consumer_noname.py consumer_libsndfile/1.0@ --lockfile=output.lock", assert_error=True)  # Mismatch name/version
    t.run(f"create {me}/recipes/consumer_noname.py  --lockfile=output.lock", assert_error=True)  # Cannot create without name/version. TODO: Take from lockfile?
    t.run(f"install {me}/recipes/consumer_noname.py name/version@ --lockfile=output.lock")
