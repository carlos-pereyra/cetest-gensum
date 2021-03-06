from util import *

#
# The FE ASIC taxon
#
def seeder(bld, **params):
    return dataroot(bld).ant_glob("*/dsk/*/oper/feasic/*/*/check_setup/params.json")

def builder(bld, seed_node, **params):
    basedir=seed_node.parent.parent

    jparam = json.loads(seed_node.read())
    feids = [str(jparam["asic%did"%ind]) for ind in range(4)]
    bid = str(jparam["boardid"])
    ts = str(jparam["session_start_time"])
    ident = '-'.join([bid, ts])

    taxon = 'feasic'
    jq_node = jq_file(bld, taxon)
    j2_node = j2_file(bld, taxon)
    json_node = prod_file(bld, taxon, ident, format='json')
    html_node = prod_file(bld, taxon, ident, format='html')

    injester = bld.path.find_resource("feasic-summary.py")
    bld(rule="${SRC[0]} ${SRC[1]} > ${TGT}",
        source=[injester, seed_node], target=[json_node])

    subdir = install_path(taxon, "board"+bid, ts)
    reltoroot = '/'.join(['..']*len(subdir.split('/')))

    bld(rule="${YASHA} -I.. -o ${TGT[0]} -v reltoroot %s -V ${SRC[1]} ${SRC[0]}" % reltoroot,
        source=[j2_node, json_node], target=[html_node])
        
    out = os.path.join("${PREFIX}", subdir)
    bld.install_as(os.path.join(out, "index.html"), html_node)

    png_nodes = basedir.ant_glob("*/*.png")
    if png_nodes:
        bld.install_files(out, png_nodes)

    return dict(ident=ident, serial=bid, feids=feids, timestamp=ts, board_id=bid, 
                json_node = json_node, html_node=html_node, png_nodes = png_nodes,
                html_subdir = subdir)


