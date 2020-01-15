import os
import re
import sys
import platform
import subprocess
import urllib.request
import shutil


from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

root_dir = os.path.dirname(os.path.realpath(__file__))

blossom5_url = "https://pub.ist.ac.at/~vnk/software/blossom5-v2.05.src.tar.gz"
blossom5_fn = os.path.join(root_dir, "blossom5-v2.05.src.tar.gz")
lib_dir = os.path.join(root_dir, "lib")
blossom5_dir = os.path.join(lib_dir, "blossom5-v2.05.src")

if not os.path.isfile(os.path.join(blossom5_dir, "PerfectMatching.h")):
    if not os.path.isfile(blossom5_fn):
        try:
            with urllib.request.urlopen(blossom5_url) as r, open(blossom5_fn, 'wb') as f:
                shutil.copyfileobj(r, f)
        except:
            print("Failed to download Blossom5 dependency, aborting installation.")
            raise
    shutil.unpack_archive(blossom5_fn, lib_dir)
    if os.path.isfile(blossom5_fn):
        os.remove(blossom5_fn)


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

setup(
    name='mwpm',
    version='0.0.1',
    author='Oscar Higgott',
    description='A C++ implementation of the Minimum Weight Perfect Matching decoder, with Python bindings.',
    ext_modules=[CMakeExtension('mwpm._cpp_mwpm')],
    packages=find_packages("src"),
    package_dir={'':'src'},
    cmdclass=dict(build_ext=CMakeBuild),
    install_requires=['scipy', 'numpy'],
    zip_safe=False,
)