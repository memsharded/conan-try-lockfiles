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
    t.run(f"create {me}/recipes/consumer_flac.py consumer_flac/1.0@")
    t.run(f"create {me}/recipes/consumer_libsndfile.py consumer_libsndfile/1.0@")

    # Let's create some 'flac' versions and store lockfiles
    flac_versions = ["1.0", "2.0", "3.0"]
    flac_locks = []
    for it in flac_versions:
        flac_lockfile = f"flac_{it}.lock"
        t.run(f"create {me}/recipes/flac.py flac/{it}@")
        t.run(f"lock create --reference flac/{it}@ --lockfile-out {flac_lockfile}")
        flac_locks.append(flac_lockfile)

    # A new 'flac' is available, also a new 'ogg' 
    t.run(f"create {me}/recipes/ogg.py ogg/2.0@")

    # I'm a 'libsndfile' developer, but I use the 'consumer_libsndfile' to run and test
    for version, flac_lock in zip(flac_versions, flac_locks):
        consumer_libsndfile_lockfile = f"consumer_libsndfile_{version}.lock"
        t.run(f"lock create --reference consumer_libsndfile/1.0@ --lockfile {flac_lock} --lockfile-out {consumer_libsndfile_lockfile}")
        t.run(f"install consumer_libsndfile/1.0@ --lockfile {consumer_libsndfile_lockfile} --lockfile-out={consumer_libsndfile_lockfile}.out --build=missing")
        assert 'ogg/2.0' not in t.out


    # EXTRA BALL: algorithm to compute the graph based on binaries that are available
    #   - the developer has one objective: use a new 'libsndfile' version
    t.run(f"export {me}/recipes/libsndfile.py libsndfile/2.0@")
    #   - this is the command they want to run, they can ONLY AFFORD to compile 'libsndfile' and 'consumer_libsndfile'
    cmd = "install consumer_libsndfile/1.0@ --build=libsndfile --build=consumer_libsndfile"
    #   - they cannot use new 'ogg/2.0' because it will force to compile 'flac' and 'vorbis'
    t.run(cmd, assert_error=True)
    assert "flac/3.0: WARN: Can't find a 'flac/3.0' package" in t.out

    # Conan can know which flac/* has binaries available and matches the version range, and can retrieve the lockfiles (stored together with the binary)
    flac_available = [(f"flac/{v}", lck) for v, lck in zip(flac_versions, flac_locks)]
    #   - iterate existing binaries, choose the first one valid
    for version, flac_lock in flac_available:
        sys.stdout.write(f"Try if {version} validates the graph...\n")
        try:
            t.run(f"lock create --reference=consumer_libsndfile/1.0@ --lockfile={flac_lock} --lockfile-out=tmp")
            t.run(f"{cmd} --lockfile=tmp --lockfile-out=tmp2")
            #t.run(f"install consumer_libsndfile/1.0@ --lockfile=tmp --lockfile-out=tmp2 --build=libsndfile --build=consumer_libsndfile")
        except Exception as e:
            sys.stdout.write(f" - no: {e}\n")
        else:
            sys.stdout.write(f" - yes\n")
            break
    else:
        sys.stderr.write(f"No flac version is available that satisfies the graph\n")

