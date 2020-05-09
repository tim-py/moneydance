#!/usr/bin/env python
# Open dataset in Moneydance
# click window - open moneybot console
# click on load and choose this file
# click on run
# This will change the current dataset to master
from com.infinitekind.moneydance.model import *

import sys
import time

# get the default environment variables, set by Moneydance
print "The Moneydance app controller: %s"%(moneydance)
print "The current data set: %s"%(moneydance_data)
print "The UI: %s"%(moneydance_ui)

moneydance_data.getLocalStorage().put("_is_master_node", True)
