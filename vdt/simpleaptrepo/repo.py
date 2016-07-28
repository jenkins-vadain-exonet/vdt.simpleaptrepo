from glob import glob
import os
import subprocess


from vdt.simpleaptrepo.config import Config


def export_pubkey(path, gpgkey):
    key_path = os.path.join(path, 'keyfile')
    cmd = "/usr/bin/gpg --yes --output %s --armor --export %s" % (
        key_path, gpgkey)
    subprocess.check_output(cmd, shell=True)
    print "Exported key %s to %s" % (gpgkey, key_path)


def sign_packages(path, gpgkey):
    # sign packages
    for deb_file in glob(os.path.join(path, "*.deb")):
        # TODO: check if package is signed!!
        print "Signed package %s" % deb_file
        subprocess.check_output(
            "/usr/bin/dpkg-sig -k %s --sign builder %s" % (gpgkey, deb_file),
            shell=True)


def create_package_index(path):
    print "Creates Packages"
    subprocess.check_output(
        "/usr/bin/apt-ftparchive packages . > Packages", shell=True, cwd=path)
    print "Creates Packages.gz"
    subprocess.check_output(
        "/bin/gzip -c Packages > Packages.gz", shell=True, cwd=path)


def create_signed_releases_index(path, gpgkey):
    print "Create Release"
    subprocess.check_output(
        "/usr/bin/apt-ftparchive release . > Release", shell=True, cwd=path)
    print "Create InRelease"
    subprocess.check_output(
        "/usr/bin/gpg --yes -u 0x%s --clearsign -o InRelease Release" % (
            gpgkey), shell=True, cwd=path)
    print "Create Reales.gpg"
    subprocess.check_output(
        "/usr/bin/gpg --yes -u 0x%s -abs -o Release.gpg Release" % (
            gpgkey), shell=True, cwd=path)


class SimpleAPTRepo(Config):

    def add_repo(self, name, path, gpgkey=""):
        if not os.path.exists(path):
            raise ValueError("Path does not exists!")

        repo_dir = os.path.abspath(os.path.join(path, name))
        if os.path.exists(repo_dir):
            raise ValueError("Directory %s already exists!" % repo_dir)

        os.mkdir(repo_dir)

        self.add_repo_config(name, path=repo_dir, gpgkey=gpgkey)

    def add_component(self, name, component):
        repo_cfg = self.get_repo_config(name)
        path = os.path.join(repo_cfg['path'], component)
        if os.path.exists(path):
            raise ValueError("Directory %s already exists!" % path)

        os.mkdir(path)

    def get_component_path(self, name, component):
        repo_cfg = self.get_repo_config(name)
        path = os.path.join(repo_cfg.get('path'), component)
        if not os.path.exists(path):
            raise ValueError("Component '%s' does not exist!" % component)
        return path

    def list_repos(self):
        result = []
        for section in self.sections:
            repo = {}
            repo_cfg = self.get_repo_config(section)
            if repo_cfg.get('gpgkey'):
                section = "%s (gpgkey: %s)" % (section, repo_cfg.get('gpgkey'))
            repo['name'] = section
            repo['components'] = os.listdir(repo_cfg.get('path'))
            result.append(repo)
        return result

    def update_component(self, path, gpgkey=None):
        if gpgkey is not None:
            # export keyfile
            export_pubkey(path, gpgkey)
            sign_packages(path, gpgkey)

        create_package_index(path)

        if gpgkey is not None:
            create_signed_releases_index(path, gpgkey)
