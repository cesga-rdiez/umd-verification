# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# import pwd
#
# from umd import api
# from umd import base
# from umd.base.configure.yaim import YaimConfig
# from umd import system
# from umd import utils
#
#
# class StormDeploy(base.Deploy):
#     """Single-node Storm deployment."""
#
#     pre_validate_pkgs = ["storm-srm-client", "uberftp", "curl", "myproxy",
#                          "voms-clients", "lcg-util"]
#
#     def __init__(self):
#         metapkg = ["emi-storm-backend-mp", "emi-storm-frontend-mp",
#                    "emi-storm-globus-gridftp-mp"]
#         nodetype = ["se_storm_backend", "se_storm_frontend",
#                     "se_storm_gridftp"]
#         if system.distro_version == "redhat5":
#             metapkg.append("emi-storm-gridhttps-mp")
#             nodetype.append("se_storm_gridhttps")
#             self.pre_validate_pkgs.append("python26-requests")
#         elif system.distro_version == "redhat6":
#             metapkg.append("storm-webdav")
#             nodetype.append("se_storm_webdav")
#         super(StormDeploy, self).__init__(
#             name="storm",
#             need_cert=True,
#             has_infomodel=True,
#             metapkg=metapkg,
#             cfgtool=YaimConfig(
#                 nodetype=nodetype,
#                 siteinfo=["site-info-storm.def"]),
#             qc_specific_id="storm")
#
#     def pre_install(self):
#         api.info("PRE-install actions.")
#
#         try:
#             pwd.getpwnam("storm")
#         except KeyError:
#             utils.runcmd("/usr/sbin/adduser -M storm")
#
#         api.info("users storm and gridhttps added")
#         api.info("END of PRE-install actions.")
#
#     def pre_config(self):
#         api.info("PRE-config actions.")
#
#         utils.install("ntp")
#         api.info("<ntp> installed.")
#
#         utils.runcmd("mount -o remount,acl,user_xattr /")
#         api.info("Enabled ACLs and Extended Attribute Support in /")
#
#         api.info("END of PRE-config actions.")
#
#     def pre_validate(self):
#         api.info("PRE-validate actions.")
#
#         utils.install(self.pre_validate_pkgs)
#         api.info("<%s> installed." % ", ".join(self.pre_validate_pkgs))
#
#         api.info("END of PRE-validate actions.")
#
#
# storm = StormDeploy()
pass
