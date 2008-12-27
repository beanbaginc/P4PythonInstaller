#!/usr/bin/env python
import ftplib
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile


p4api_version = "08.2"

perforce_hostname = "ftp.perforce.com"
perforce_path = "/perforce/r%s" % p4api_version
p4python_path = "%s/tools" % perforce_path


def download(paths):
    """
    Downloads files from the Perforce FTP server.
    """
    ftp = ftplib.FTP(perforce_hostname)
    ftp.login()

    for path in paths:
        filename = path.rsplit("/", 1)[1]
        print "Downloading %s..." % filename
        ftp.retrbinary("RETR %s" % path,
                       open(filename, "wb").write)

    ftp.quit()


def extract(filename):
    """
    Extracts a tarball into the current directory, and returns the directory
    name where the files were extracted.
    """
    print "Extracting %s..." % filename
    tar = tarfile.open(filename, "r:gz")
    dirname = tar.getnames()[0].rstrip("/")
    tar.extractall()
    tar.close()

    return dirname


def get_p4api_path():
    """
    Returns the p4api.tgz download path, based on the platform information.
    """
    arch = platform.machine()

    if re.match("i\d86", arch):
        arch = "x86"
    elif arch == "x86_64":
        arch = "x86_64"
    else:
        sys.stderr.write("Unsupported system architecture: %s\n" % arch)
        sys.exit(1)

    osname = platform.system()

    if osname == "Linux":
        linuxver = platform.release()
        if linuxver.startswith("2.6"):
            osname = "linux26"
        elif linuxver.startswith("2.4"):
            osname = "linux24"
        else:
            sys.stderr.write("Unsupported Linux version: %s" % linuxver)
            sys.exit(1)
    elif osname == "Windows":
        # TODO: Download and run the Windows installer.
        print "Download the Windows installer at:"
        print "http://public.perforce.com/guest/robert_cowham/perforce/API/python/index.html"
        sys.exit(1)
    elif osname == "Darwin":
        # XXX: "darwin" or "macosx" ?
        osname = "macosx104"
    else:
        # TODO: Should support Solaris/OpenSolaris
        sys.stderr.write("Unsupported operating system: %s" % osname)
        sys.exit(1)

    return "%s/bin.%s%s" % (perforce_path, osname, arch)


def main():
    p4api_path = get_p4api_path()

    curdir = os.getcwd()

    tmpdir = tempfile.mkdtemp()
    os.chdir(tmpdir)

    download(["%s/p4api.tgz" % p4api_path,
              "%s/p4python.tgz" % p4python_path])

    p4api_dir = os.path.abspath(extract("p4api.tgz"))
    p4python_dir = extract("p4python.tgz")

    os.chdir(p4python_dir)

    # Generate the setup.cfg file.
    fp = open("setup.cfg", "w")
    fp.write("[p4python_config]\n")
    fp.write("p4_api=%s" % p4api_dir)
    fp.close()

    args = []

#    for arg in sys.argv[1:]:
#        if arg.startswith("bdist"):
#            args.append("install")
#        elif arg.
#        else:
#            args.append(arg)

    p = subprocess.Popen([sys.executable, "setup.py", "install"])
    rc = p.wait()

    os.chdir(curdir)

    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
