from setuptools import setup
from setuptools.command.install import install
import os
import os.path as p
import platform
import shutil
import stat

# ------------------------------------------------------------------------------
# Custom settings:
# ------------------------------------------------------------------------------
version = '2.6'
url = 'https://anaconda.org/conda-forge/pandoc/{version}/download/{os}-64/pandoc-{version}-{build}.tar.bz2'
tmp = 'tmp'
spec = dict(
    Windows=dict(
        os='win', build=0, move=[('Library/bin/*', tmp)],
        hash='04f1a3e6b05714627872fade3301c3cb057494282ce3a5cb8febab0bc29317d4'),
    Linux=dict(
        os='linux', build=0, move=[('bin/*', tmp)],
        hash='344b57466e76d50e5519823ba385aae50fc42683c933d6c17d9f47fed41cfbf9'),
    Darwin=dict(
        os='osx', build=0, move=[('bin/*', tmp)],
        hash='92319289025f2d79a2a69292364121c8e171c57d734a82fa5b2f1eca86e8f9ad'),
)[platform.system()]
spec.setdefault('url', url.format(version=version, **spec))

                                  
class PostInstallCommand(install):
    def run(self):
        excract_tar_and_move_files(**spec)

        from_ = p.join(p.dirname(p.abspath(__file__)), tmp)
        to = self.install_scripts
        os.makedirs(to, exist_ok=True)

        for file in os.listdir(from_):
            file_path = p.join(from_, file)
            # there should be no folders anyway:
            if p.isfile(file_path):
                if os.name != 'nt':
                    st = os.stat(file_path)
                    os.chmod(file_path, st.st_mode | stat.S_IEXEC)
                shutil.move(file_path, p.join(to, file))

        install.run(self)


# ------------------------------------------------------------------------------


def sha256(filename):
    """ https://stackoverflow.com/a/44873382/9071377 """
    import hashlib

    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def excract_tar_and_move_files(url, hash, move, **kwargs):
    """
    Moves relative to the setup.py dir. Can download more packages
    if the target archive contains setup.py

    * ``url`` should be of the form z/name.x.y.gz
      (gz, bz2 or other suffix supported by the tarfile module).
    * ``move`` contains pairs of dirs, first one can be of the form ``dir/*``
      (it means moving contents instead of moving the dir itself).
      First dir is in the extracted archive,
      second dir is in the same folder as setup.py
    """
    import sys
    import tarfile
    from subprocess import call, run, PIPE
    import tempfile

    dirpath = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(dirpath)

    call([sys.executable, "-m", "pip", "download", url], stdout=PIPE, stderr=PIPE)
    filename = url.split('/')[-1]
    ext = p.splitext(filename)[1][1:]
    if sha256(filename) != hash:
        raise RuntimeError(f'SHA256 hash does not match for {filename}')
    with tarfile.open(filename, f"r:{ext}") as tar:
        tar.extractall()

    for from_, to in move:
        if from_.endswith('/*') or from_.endswith(r'\*'):
            from_ = from_[0:-2]
        else:
            to = p.join(to, p.basename(from_))
        from_ = p.abspath(p.normpath(from_))
        to = p.normpath(p.join(p.dirname(p.abspath(__file__)), to))
        os.makedirs(to, exist_ok=True)
        for smth in os.listdir(from_):
            shutil.move(p.join(from_, smth), to)
    os.chdir(cwd)
    shutil.rmtree(dirpath)


setup(
    name='py-pandoc',
    version=version,
    cmdclass={'install': PostInstallCommand},

    description='Pandoc in pip and conda',
    url='https://github.com/kiwi0fruit/py-pandoc',
    author='kiwi0fruit',
    author_email='peter.zagubisalo@gmail.com',
    license='GPLv2+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
)
