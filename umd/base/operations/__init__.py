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

import json

import requests

from umd import api
from umd.common import qc
from umd import config


class Operations(object):
    @qc.qcstep("QC_MON_1", "Service Probes")
    def qc_mon_1(self):
        """Service Probes."""
        if config.CFG["qc_mon_capable"]:
            headers = {"content-type": "application/json"}
            url = "http://%s/siteurls" % config.CFG["umdnsu_url"]
            data = {"name": config.CFG["name"].upper()}

            try:
                resp = requests.post(url,
                                     data=json.dumps(data),
                                     headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if data["enabled"]:
                        # FIXME Need to provide the Nagios URL where the host
                        # will be monitored
                        api.ok("LDAP URL added:'%s %s'" % (data["prefix"],
                                                           data["url"]))
                    else:
                        api.warn("Could not add LDAP URL: %s" % resp.text)
                else:
                    api.fail("Response error received from server (%s): '%s'"
                             % (resp.status_code, resp.text))
            except requests.exceptions.ConnectionError:
                api.fail("Could not connect to Nagios at '%s'" % url)
        else:
            api.na("Product cannot be tested by Nagios.")

    @qc.qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_mon_1()
