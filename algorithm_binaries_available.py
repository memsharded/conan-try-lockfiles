import os
import shutil
import sys
from conans.test.utils.tools import NO_SETTINGS_PACKAGE_ID, TestClient
from conans import tools

me = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")


if __name__ == '__main__':
    # Configure a test client to play with
    working_dir = os.path.join(me, '_working_dir')
    shutil.rmtree(working_dir, ignore_errors=True)

    t = TestClient(path_with_spaces=False, current_folder=working_dir)
    t.run("config set general.default_package_id_mode=recipe_revision_mode")
    t.run("config set general.revisions_enabled=1")

    # I'm a developer of 'libsndfile', but to test my work I need to compile
    # 'consumer_libsndfile'. I have a real pain in my development workflow, the
    # library 'flac' is a PITA and it takes hours to build.

    flac_binaries_in_cache = []

    # Populate the cache
    t.run(f"export {me}/recipes/pyreq.py pyreq/0.1@")
    t.run(f"create {me}/recipes/ogg.py ogg/0.0@")
    t.run(f"create {me}/recipes/flac.py flac/1.0@ --lockfile-out=flac_1.0-ogg_0.0.lock")
    flac_binaries_in_cache.append(('flac/1.0', 'flac_1.0-ogg_0.0.lock'))
    
    t.run(f"create {me}/recipes/ogg.py ogg/1.0@")
    t.run(f"create {me}/recipes/flac.py flac/1.0@ --lockfile-out=flac_1.0-ogg_1.0.lock")
    flac_binaries_in_cache.append(('flac/1.0', 'flac_1.0-ogg_1.0.lock'))
    
    t.run(f"create {me}/recipes/vorbis.py vorbis/1.0@")
    t.run(f"create {me}/recipes/libsndfile.py libsndfile/1.0@")
    t.run(f"create {me}/recipes/consumer_libsndfile.py consumer_libsndfile/1.0@")

    # Some unrelated development modifies my cache and retrieves new versions of ogg
    t.run(f"create {me}/recipes/ogg.py ogg/2.0@")
    t.run(f"create {me}/recipes/ogg.py ogg/3.0@")
    t.run(f"create {me}/recipes/vorbis.py vorbis/1.0@")


    # When I came back to work in 'libsndfile', 'flac' is no longer avaialbe as binary because Conan resolves to 'ogg/3.0'
    #   - I develop a new version of 'libsndfile'
    t.run(f"export {me}/recipes/libsndfile.py libsndfile/2.0@")
    #   - I want to build only 'libsndfile' and 'consumer_libsndfile'
    cmd = "install consumer_libsndfile/1.0@ --build=libsndfile --build=consumer_libsndfile"
    #   - Current content in the cache fail
    t.run(cmd, assert_error=True)
    assert "ERROR: Missing prebuilt package for 'flac/1.0'" in t.out

    # RFC: Build the graph using binaries available in the cache
    report = []
    lockfile_selected = None
    for flac_ref, flac_lockfile in flac_binaries_in_cache:
        msg = f"Try if {flac_ref} with {flac_lockfile} validates the graph..."
        report.append(msg)
        try:
            t.run(f"lock create --reference=consumer_libsndfile/1.0@ --lockfile={flac_lockfile} --lockfile-out=tmp")
            t.run(f"{cmd} --lockfile=tmp --lockfile-out=product.lock")
            lockfile_selected = "product.lock"
        except Exception as e:
            msg = f" - no"
            report.append(msg)
        else:
            msg = f" - yes"
            report.append(msg)
            break
    else:
        msg = f"No flac version is available that satisfies the graph\n"
        report.append(msg)

    sys.stdout.write("\n".join(report))
    sys.stdout.write("\n")
    sys.stdout.write(f"Successful lockfile in '{lockfile_selected}'\n")

    content = tools.load(os.path.join(current_folder, lockfile_selected))
    assert "flac/1.0" in content
    assert "ogg/1.0" in content
