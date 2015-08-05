from fabric import api as fabric_api
from fabric import tasks

from umd import api
from umd.base.configure import YaimConfig
from umd.base.infomodel import InfoModel
from umd.base.installation import Install
from umd.base.operations import Operations
from umd.base.security import Security
from umd.base import utils as butils
from umd.base.validate import Validate
from umd import config
from umd import utils


class Deploy(tasks.Task):
    """Base class for UMD deployments."""
    def __init__(self,
                 name,
                 doc=None,
                 metapkg=[],
                 need_cert=False,
                 has_infomodel=True,
                 nodetype=[],
                 siteinfo=[],
                 qc_mon_capable=False,
                 qc_specific_id=None,
                 qc_step={},
                 exceptions={},
                 dryrun=False):
        """Arguments:

                name: Fabric command name.
                doc: docstring that will appear when typing `fab -l`.
                metapkg: list of UMD metapackages to install.
                need_cert: whether installation type requires a signed cert.
                has_infomodel: whether the product publishes information
                               about itself.
                nodetype: list of YAIM nodetypes to be configured.
                siteinfo: list of site-info files to be used.
                qc_specific_id: ID that match the list of QC-specific checks
                    to be executed. The check definition must be included in
                    etc/qc_specific.yaml
                exceptions: documented exceptions for a given UMD product.
        """
        self.name = name
        if doc:
            self.__doc__ = doc
        self.metapkg = utils.to_list(metapkg)
        self.need_cert = need_cert
        self.has_infomodel = has_infomodel
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.qc_specific_id = qc_specific_id
        self.exceptions = exceptions
        self.cfgtool = None
        self.ca = None
        self.installation_type = None  # FIXME default value?
        self.qc_mon_capable = qc_mon_capable
        self.qc_envvars = {}
        self.qc_step = qc_step
        self.dryrun = dryrun

    def pre_install(self):
        pass

    def post_install(self):
        pass

    def pre_config(self):
        pass

    def post_config(self):
        pass

    def pre_validate(self):
        pass

    def post_validate(self):
        pass

    def _install(self, **kwargs):
        self.pre_install()
        Install().run(**kwargs)
        self.post_install()

    def _security(self, **kwargs):
        Security().run(**kwargs)

    def _infomodel(self, **kwargs):
        InfoModel().run(**kwargs)

    def _operations(self, **kwargs):
        Operations().run(**kwargs)

    def _validate(self, **kwargs):
        self.pre_validate()
        Validate().run(**kwargs)
        self.post_validate()

    def run(self, **kwargs):
        """Takes over base deployment.

            installation_type
                Type of installation: 'install' (from scratch) or 'update'.
            repository_url
                Repository path with the verification content.
                Could pass multiple values by prefixing with 'repository_url'.
            epel_release
                Package URL with the EPEL release.
            umd_release
                Package URL with the UMD release.
            igtf_repo
                Repository for the IGTF release.
            yaim_path
                Path pointing to YAIM configuration files.
            log_path
                Path to store logs produced during the execution.
            qcenv_*
                Pass environment variables needed by the QC specific checks.
            qc_step
                Run a given set of Quality Criteria steps.
                Works exactly as 'repository_url' i.e. to pass more than one
                QC step to run, prefix it as 'qc_step'.
        """
        # Set class attributes
        config.CFG.update(utils.get_class_attrs(self))
        config.CFG.update(kwargs)

        # Show configuration summary
        utils.show_exec_banner()

        # Configuration tool
        if self.nodetype and self.siteinfo:
            config.CFG["cfgtool"] = YaimConfig(
                pre_config=self.pre_config,
                post_config=self.post_config)
        # else:
        #     raise exception.ConfigException("Configuration not implemented.")

        # Certification Authority
        if self.need_cert:
            utils.install("ca-policy-egi-core")
            config.CFG["ca"] = butils.OwnCA(
                domain_comp_country="es",
                domain_comp="UMDverification",
                common_name="UMDVerificationOwnCA")
            config.CFG["ca"].create(
                trusted_ca_dir="/etc/grid-security/certificates")

        # Workflow
        if config.CFG["qc_step"]:
            for step in config.CFG["qc_step"]:
                k, v = (step.rsplit('_', 1)[0], step)
                try:
                    step_mappings = {
                        "QC_DIST": self._install,
                        "QC_UPGRADE": self._install,
                        "QC_SEC": self._security,
                        "QC_INFO": self._infomodel,
                        "QC_FUNC": self._validate}
                except KeyError:
                    fabric_api.abort(api.fail(("%s step not found in the "
                                               "Quality Criteria" % k)))

                step_mappings[k](**{"qc_step": v})
        else:
            # QC_INST, QC_UPGRADE
            self._install()

            # QC_SEC
            self._security()

            # QC_INFO
            self._infomodel()

            # QC_MON
            self._operations()

            # QC_FUNC
            self._validate()
