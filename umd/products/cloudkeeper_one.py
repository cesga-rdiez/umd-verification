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

from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config


class ClodkeeperOneDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "xxxx: yyyyy",
            "zzzz: ttttt"]
        self.cfgtool.extra_vars = extra_vars


cloudkeeper_one = CloudkeeperOneDeploy(
    name="cloudkeeper-one",
    doc="cloudkeeper/cloudkeeper-one deployment using Ansible.",
    # has_infomodel=True,
    cfgtool=AnsibleConfig(
##        role="https://github.com/egi-qc/ansible-cloudkeeper-one",
        role="https://github.com/cesga-rdiez/ansible-cloudkeeper-one",
        checkout="umd",
        tags=["untagged", "cmd"]),
    qc_specific_id="cloudkeeper-one")

