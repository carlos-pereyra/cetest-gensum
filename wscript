#!/usr/bin/env python

# prepare installation area:
# $ ln -s /dsk/1/data/sync-json $HOME/public_html/data

# prepare dev area
# $ virtualenv --system-site-packages -p python2 venv
# $ source venv/bin/activate
# $ pip install -r requirements.txt 
# $ ./waf configure --prefix=$HOME/public_html/summary
# $ ./waf build install

# Links in the HTML assume data/ and summary/ are siblings.

# This build follows a structure of a /taxonomy/ with a dependency
# tree between its taxa.  An /instance/ of one taxon consists of
# various file /products/ built by this wscript, a subset of which get
# installed to the prefix.  An instance product hase these attributes:

# - ident :: an instance identifier which is typically a timestamp and/or a part serial number.
# - schema :: labels the organization of the file content gives a hint of semantic purpose.
# - format :: describes how the bits are arranged in the file (eg, HTML, JSON, PNG).  One schema may have multiple file formats.

# The set of instance product files generally consist of one
# intermediate /summary/ (a schema) JSON file holding all info about
# the taxon instance, and one /summary/ HTML file generated by
# applying a taxon-specific Jinja2 file against this HTML.

# Each taxon instance has a builder function.  This builder accepts
# the Waf build context, a "seed" node and a number of parameters.  It
# constructs the Waf tasks needed to create all products of its
# instance.  It also returns a metadata dictionary which may be used
# for constructing others (through their parameters) as determined by
# the wscript code.


# The taxonmy includes

taxa = [
#    "adcasic",                  # a sample result of the ADC ASIC test
#    "feasic",                   # a sample result of the FE ASIC test
    "femb",                     # a sample result of the FEMB test
#    "adcid",                    # collect on ADC ASIC ident
#    "feid",                     # collect on FE ASIC ident
#    "fembid",                   # collect on FEMB iden
#    "adcasicbid",               # collect on ADC ASIC test board ident
#    "feasicbid",                # collect on FE ASIC test board ident
]

# Note, products in *id taxa depend on produts of the previous.

import os
from collections import defaultdict

def options(opt):
    opt.add_option('--data-root', action='store', default="/dsk/1/data/sync-json",
                   help='Point to the root directory holding the data')
    pass

def configure(cfg):
    cfg.find_program("jq",var="JQ",mandatory=True)
    cfg.find_program("yasha",var="YASHA",mandatory=True)


import importlib

def build(bld):

    taxa_dat = defaultdict(list) # hold metadata keyed by taxon name

    for taxon in taxa:
        mod = importlib.import_module("taxon.%s" % taxon)

        print ("Building for %s" % taxon)

        for count, seed in enumerate(mod.seeder(bld, **taxa_dat)):
            dat = mod.builder(bld, seed, **taxa_dat)
            if not dat:
                continue
            taxa_dat[taxon].append(dat)
            if count > 10:
                break           # keep fast for testing
