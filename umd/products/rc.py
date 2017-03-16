import re
import urllib2
import xml.etree.ElementTree as ET

from umd import api
from umd import base
from umd import config
from umd.products import utils as product_utils
from umd import system
from umd import utils


class RCDeploy(base.Deploy):
    from umd.products import bdii, gram5, globus, gridsite, wms, fts    # NOQA
    from umd.products import glexec, cream, arc, ui, canl, xrootd       # NOQA
    from umd.products import storm, argus, dcache, ca, frontier_squid   # NOQA
    from umd.products import dpm, keystone_voms  			# NOQA
    from umd.products import cloud_info_provider                        # NOQA

    cmd_mapping = {
        "1.0.0": "mitaka",
    }

    product_mapping = {
        "apel": ["apel-parsers", "apel-server", "apel-client", "apel-lib"],
        "apel-ssm": ["apel-ssm"],
        "arc": arc.arc_ce.metapkg,
        "argus": argus.argus_puppet_no_metapkg.metapkg,
        "argus-pap": argus.argus_puppet_no_metapkg.metapkg,
        "bdii core": ["bdii"],
        "bdii site": bdii.bdii_site_puppet.metapkg,
        "bdii top": bdii.bdii_top_puppet.metapkg,
        "bdii-infoprovider": cloud_info_provider.package,
        "canl": canl.canl.metapkg,
        "canl32": canl.canl.metapkg,
        "cgsi-gsoap": ["CGSI-gSOAP"],
        "classads-libs": ["classads"],
        # FIXME(orviz): Uncomment it when the repository cmd-os-1 exists
        # "cmd-release": ["cmd-os-release"],
        "cream": cream.standalone.metapkg,
        "cream-ge": cream.gridenginerized.metapkg,
        "cream-ge-utils": cream.gridenginerized.metapkg,
        "cream-ge module": cream.gridenginerized.metapkg,
        "cream lsf": cream.lsfized.metapkg,
        "cream-lsf": cream.lsfized.metapkg,
        "cream-slurm": cream.slurmized.metapkg,
        "cvmfs": ["cvmfs"],
        "davix": ui.ui_gfal.metapkg,
        "dcache": dcache.dcache.metapkg,
        "dcache-srmclient": dcache.dcache.metapkg,
        "dcache-srm-client": dcache.dcache.metapkg,
        "dmlite": ["python-dmlite", "dmlite-shell", "dmlite-libs"],
        "dpm": dpm.dpm_1_8_10.metapkg,
        "dpm-argus": ["dpm-argus"],
        "edg-mkgrid": ["edg-mkgridmap"],
        "emi ui": ui.ui.metapkg,
        "emi-ui": ui.ui.metapkg,
        "emi-wn": ["emi-wn"],
        "fetch-crl": ca.crl.metapkg,
        "fts3": fts.fts.metapkg,
        "fts3-ext": fts.fts.metapkg,
        "gateway": ["unicore-gateway"],
        "gfal2": ui.ui_gfal.metapkg,
        "gfal2-python": ui.ui_gfal.metapkg,
        "gfal2-utils": ui.ui_gfal.metapkg,
        "gfal/lcg_util": ["lcg-util"],
        "gfal2-plugin-xrootd": ui.ui_gfal.metapkg,
        "glexec": glexec.glexec_wn.metapkg,
        "glexec-wn": glexec.glexec_wn.metapkg,
        "globus":
            globus.gridftp.metapkg + globus.default_security.metapkg,
        "globus-32-bit":
            globus.gridftp.metapkg + globus.default_security.metapkg,
        "globus-default-security": globus.default_security.metapkg,
        "globus info provider service": ["globus-info-provider-service"],
        "globus gsissh":
            globus.gridftp.metapkg + globus.default_security.metapkg,
        "globus-gridftp-32": globus.gridftp.metapkg,
        "globus-net-manager": ["globus-net-manager"],
        "gram5": gram5.gram5.metapkg,
        "gridftp": globus.gridftp.metapkg,
        "gridsafe": ["ige-meta-gridsafe"],
        "gridsite": gridsite.gridsite.metapkg,
        "gridway": ["ige-meta-gridway"],
        "json-c": ["json-c"],
        "keystone-voms": ["python-keystone-voms"],
        "lb": wms.lb.metapkg,
        "lcas-lcmaps-gt4": ["lcas-lcmaps-gt4-interface"],
        "lcas": ["lcas", "lcas-lcmaps-gt4-interface", "lcas-plugins-basic", "lcas-plugins-check-executable", "lcas-plugins-voms"],
        "lcmaps": ["lcmaps"],
        "lcmaps-plugins": ["lcmaps-plugins-basic", "lcmaps-plugins-c-pep", "lcmaps-plugins-voms", "lcmaps-plugins-vo-ca-ap"],
        "lcmaps-plugins-vo-ca-ap": ["lcmaps-plugins-vo-ca-ap"],
        "lfc": ["lfc", "lfc-server-mysql"],
        "myproxy": ui.ui_myproxy.metapkg,
        "occi": ["python-ooi"], 
        "site-bdii": bdii.bdii_site_puppet.metapkg,
        "squid": frontier_squid.frontier_squid.metapkg,
        "storm": storm.storm.metapkg,
        "srm-ifce": ui.ui_gfal.metapkg,
        "qcg-comp": ["qcg-comp"],
        "qcg-ntf": ["qcg-ntf"],
        "top-bdii": bdii.bdii_top_puppet.metapkg,
        "tsi": ["unicore-tsi-nobatch"],
        "umd-3 repository configuration": ["umd-release"],
        "umd-release": ["umd-release"],
        "voms": ["voms-clients"],
        "voms-admin": ["voms-admin-client", "voms-admin-server"],
        "voms-admin-server": ["voms-admin-server"],
        "voms-clients": ["voms-clients"],
        "voms-server": ["voms-server"],
        "wms": wms.wms.metapkg,
        "wms-utils": wms.wms_utils.metapkg,
        "wn-slurm": ["emi-slurm-client"],
        "xuudb": ["unicore-xuudb"],
        "xroot": xrootd.xrootd.metapkg,
        "xroot-libs": xrootd.xrootd.metapkg,
        "yaim-core": ["glite-yaim-core"],
    }

    def _get_callback(self, url, from_major_release=None):
        """Get the callback URL from UMD repository feeds.

        :url: URL of the UMD repository feed.
        :from_major_release: Get all callbacks matching major release number.
        """
        response = urllib2.urlopen(url)
        txt = response.read()
        root = ET.fromstring(txt)

        if config.CFG["rc_release"].startswith("CMD"):
            distro_type = "CMD-OS"
        elif config.CFG["rc_release"].startswith("UMD"):
            distro_type = "UMD"
        else:
            api.fail("Distribution type '%s' not known"
                     % config.CFG["rc_release"],
                     stop_on_error=True)
        l = []
        for p in root.iter('item'):
            s = re.search("Release: (%s-\d*\.\d*\.\d*)" % distro_type,
                          p.find("title").text)
            if s:
                release = s.groups()[0]
                cb = p.find("distroAPICallBack").text
                if from_major_release:
                    major_release_no = config.CFG["rc_release"].split('.')[0]
                    if release.startswith(major_release_no):
                        l.append(cb)
                else:
                    if release == config.CFG["rc_release"]:
                        l.append(cb)
        return l

    def _get_product_list(self, urls):
        """Get the list of products given in a UMD callback url.

        :urls: List of the callback URLs.
        """
        # NOTE for scientific linux is 'sl' not 'redhat'
        if system.distro_version.startswith("redhat"):
            distro = [system.distro_version,
                      system.distro_version.replace("redhat", "sl")]
        elif system.distro_version == "ubuntu14":
            distro = [system.distro_version,
                      "ubuntu-trusty"]
        else:
            distro = [system.distro_version]
        s = set()
        for url in urls:
            response = urllib2.urlopen(url)
            txt = response.read()
            root = ET.fromstring(txt)

            for p in root.iter("product"):
                match_os = False
                for t in p.iter("target"):
                    if t.get("platform") in distro:
                        match_os = True
                if match_os:
                    s = s.union([(p.get("display"), p.get("version"))])
        return list(s)

    def pre_install(self):
        # Add repositories (and keys)
        repocount = 1
        for repo in config.CFG["repository_url"]:
            if repo.find("base") != -1:
                utils.enable_repo(repo,
                                  name="UMD RC base",
                                  priority=1)
            else:
                utils.enable_repo(repo,
                                  name="UMD RC %s" % repocount,
                                  priority=1)
                repocount += 1
        utils.add_repo_key(config.CFG["repo_keys"])
        utils.enable_repo(config.CFG["igtf_repo"])
        utils.add_repo_key(config.CFG["igtf_repo_key"])
	if config.CFG.get("cmd_release", None):
            rc_release_version = config.CFG.get("rc_release").split('-')[-1]
	    product_utils.add_openstack_distro_repos(
               self.cmd_mapping[rc_release_version])

        # Products from production
        url_production = "http://admin-repo.egi.eu/feeds/production/"
        production_products = self._get_product_list(
            self._get_callback(
                url_production,
                from_major_release=config.CFG.get("umd_release", None)))
        api.info("Products from production repository: %s"
                 % production_products)
        # Products from the candidate RC
        url_candidate = "http://admin-repo.egi.eu/feeds/candidate/"
        candidate_products = self._get_product_list(
            self._get_callback(url_candidate))
        api.info("Products from the candidate RC: %s" % candidate_products)
        # Merge them all
        products = production_products + candidate_products
        s = set()
        for product in products:
            if isinstance(product, tuple):
                _name, _version = product
                product = _name
            product = product.lower()
            try:
                s = s.union(self.product_mapping[product])
            except KeyError:
                api.warn(("Product '%s' not mapped to any package. Will not "
                          "be installed" % product))
        config.CFG["metapkg"] = list(s)

        # check_obsoletes
        if system.distro_version.startswith("redhat"):
            utils.runcmd(("echo -e \"[main]\nenabled = 1"
                          "\ncheck_obsoletes = 1\" > "
                          "/etc/yum/pluginconf.d/priorities.conf"))

    def _install(self, **kwargs):
	self.pre_install()
        if (config.CFG["rc_release"].startswith("UMD") and
            system.distro_version in ["redhat5", "redhat6", "centos7"]):
            if not utils.is_pkg_installed("epel-release"):
                utils.install_remote(config.CFG["epel_release"])
        kwargs.update({
            "ignore_repos": True,
            "ignore_verification_repos": True})
        base.installation.Install().run(**kwargs)
	self.post_install()


rc = RCDeploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    qc_step="QC_DIST_1",
)
