from umd import config
from umd import utils as base_utils


def set_umd_params(template_file, output_file):
    _distribution = config.CFG["distribution"]
    if _distribution == "umd":
        _release = config.CFG["umd_release"]
    elif _distribution == "cmd":
        _release = config.CFG["cmd_release"]
    elif _distribution == "cmd-one":
        _release = config.CFG["cmd_one_release"]

    _data = {
        "release": _release,
        "distribution": _distribution,
        "repository_file": config.CFG.get("repository_file", ""),
        "openstack_release": config.CFG.get("openstack_release", "False"),
        "igtf_repo": "False",
        "enable_testing_repo": config.CFG.get("enable_testing_repo", "False"),
        "enable_untested_repo": config.CFG.get("enable_untested_repo", "Flase"),
    }
    if config.CFG.get("need_cert", ""):
        _data["igtf_repo"] = "yes",

    base_utils.render_jinja(
        template_file,
        _data,
        output_file=output_file)
