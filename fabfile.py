
from fabric.state import output

from umd.products.argus import *
from umd.products.creamce import *
from umd.products.storm import *


output.status = False
output.stdout = False
output.warnings = False
output.running = False
output.user = True
output.stderr = False
output.aborts = True
output.debug = False
