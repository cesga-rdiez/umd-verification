from distutils import version
import os.path

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import system
from umd import utils


hiera_config = """
---
:backends:
  - yaml
:yaml:
  :datadir: /etc/puppet/hieradata
:hierarchy:
  - global
"""


class PuppetConfig(BaseConfig):
    def __init__(self,
                 manifest,
                 hiera_data=None,
                 module_from_puppetforge=[],
                 module_from_repository=[],
                 module_path=[]):
        """Runs Puppet configurations.

        :manifest: Main ".pp" with the configuration to be applied.
        :hiera_data: YAML file with hiera variables.
        :module_from_puppetforge: list of modules to be installed
                                  (from PuppetForge).
        :module_from_repository: module (repotype, repourl) tuples.
        :module_path: Extra Puppet module locations.
        """
        self.manifest = manifest
        self.hiera_data = hiera_data
        self.module_from_puppetforge = utils.to_list(module_from_puppetforge)
        self.module_from_repository = utils.to_list(module_from_repository)
        self.module_path = utils.to_list(module_path)

    def _v3_workaround(self):
        # Include hiera functions in Puppet environment
        utils.install("rubygems")
        utils.runcmd(("gem install hiera-puppet --install-dir "
                      "/etc/puppet/modules"))
        utils.runcmd("mv /etc/puppet/modules/gems/* /etc/puppet/modules/")

    def _set_hiera(self):
        if self.hiera_data:
            with open("/etc/puppet/hiera.yaml", 'w') as f:
                f.write(hiera_config)
            if not os.path.exists("/etc/puppet/hieradata"):
                utils.runcmd("mkdir /etc/puppet/hieradata")
            utils.runcmd("cp %s /etc/puppet/hieradata/global.yaml"
                         % self.hiera_data)

    def config(self, logfile=None):
        self.manifest = os.path.join(config.CFG["puppet_path"], self.manifest)
        if self.hiera_data:
            self.hiera_data = os.path.join(config.CFG["puppet_path"],
                                           self.hiera_data)

        r = utils.install("puppet", log_to_file=logfile)
        if r.failed:
            api.fail("Puppet installation failed", stop_on_error=True)

        # Puppet versions <3 workarounds
        puppet_version = utils.runcmd("facter -p puppetversion")
        if puppet_version and (version.StrictVersion(puppet_version)
           < version.StrictVersion("3.0")):
            # self._v3_workaround()
            pkg_url = config.CFG["puppet_release"]
            pkg_loc = "/tmp/puppet-release.rpm"
            r = utils.runcmd("wget %s -O %s" % (pkg_url, pkg_loc))
            if r.failed:
                api.fail("Could not fetch Puppet package from '%s'" % pkg_url,
                         stop_on_error=True)
            else:
                api.info("Fetched Puppet release package from '%s'." % pkg_url)
            utils.install(pkg_loc)
            utils.runcmd(("sed '/enabled=1/a\priority=1' "
                          "/etc/yum.repos.d/puppet*"))

            # FIXME (orviz) Remove this check when dropping redhat5 support
            if system.distro_version == "redhat5":
                pkg = ("ftp://rpmfind.net/linux/centos/5.11/os/x86_64/CentOS/"
                       "virt-what-1.11-2.el5.x86_64.rpm")
                utils.runcmd(("wget %s -O /tmp/virt-what.rpm && yum -y "
                              "install /tmp/virt-what.rpm") % pkg)

            utils.install("puppet")

        # Install modules from puppetforge/local
        for mod in self.module_from_puppetforge:
            r = utils.runcmd("puppet module install %s --force" % mod)
            if r.failed:
                api.fail("Error while installing module '%s'" % mod)
        self.module_path.append(*["/etc/puppet/modules"])

        # FIXME (orviz) This is ugly - PATCHES
        if "CERNOps-fts" in self.module_from_puppetforge:
            utils.install("patch")
            utils.runcmd("patch -p0 < etc/patches/CERNOps-fts.patch")

        module_loc = []
        for mod in self.module_from_repository:
            dirname = utils.clone_repo(*mod)
            if dirname:
                module_loc.append(dirname)
        if module_loc:
            self.module_path.append(*module_loc)

        # Hiera environment
        self._set_hiera()

        logfile = os.path.join(config.CFG["log_path"], "puppet.log")

        r = utils.runcmd(("puppet apply -l %s --modulepath %s %s "
                          "--detail-exitcodes")
                         % (logfile,
                            ':'.join(self.module_path),
                            self.manifest))
        if r.return_code == 0:
            api.info("Puppet execution ended successfully.")
        elif r.return_code == 2:
            api.info(("Puppet execution ended successfully (some warnings "
                      "though, check logs)"))
            r.failed = False
        else:
            api.fail("Puppet execution failed. More information in logs: %s"
                     % logfile)
            r.failed = True

        self.has_run = True

        return r
