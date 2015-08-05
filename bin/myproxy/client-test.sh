#!/bin/bash -eu

set -x

## Requirements:
##      A myproxy already stored in MYPROXY_SERVER with user and passphrase credentials. E.g.:
##
##              echo $MYPROXY_PASSWD | myproxy-init -S -l $MYPROXY_USER -s $MYPROXY_SERVER -m $VO
##

# ops.vo.ibergrid.eu configuration
mkdir -p ~/.voms
cat > ~/.voms/vomses << EOF 
"ops.vo.ibergrid.eu" "ibergrid-voms.ifca.es" "40001" "/DC=es/DC=irisgrid/O=ifca/CN=host/ibergrid-voms.ifca.es" "ops.vo.ibergrid.eu"
"ops.vo.ibergrid.eu" "voms01.ncg.ingrid.pt" "40001" "/C=PT/O=LIPCA/O=LIP/OU=Lisboa/CN=voms01.ncg.ingrid.pt" "ops.vo.ibergrid.eu"
EOF

VO=ops.vo.ibergrid.eu
MYPROXY_PASSWD_OTHER=test.change.passwd


function change_passphrase {
    echo -e "$1\n$2" | myproxy-change-pass-phrase -S -s $MYPROXY_SERVER -l $MYPROXY_USER
}

function destroy {
    myproxy-destroy -s $MYPROXY_SERVER -l $MYPROXY_USER
}

function info {
    myproxy-info -s $MYPROXY_SERVER -l $MYPROXY_USER
}

function retrieve {
    echo $1 | myproxy-logon -S -s $MYPROXY_SERVER -l $MYPROXY_USER -m $VO
}

if [ $# -eq 1 ]; then
    case $1 in
        retrieve)
            retrieve $MYPROXY_PASSWD
            ;;
        *)
            echo "Method '$1' not implemented"
            exit -1
            ;;
    esac
else
    retrieve $MYPROXY_PASSWD

    change_passphrase $MYPROXY_PASSWD $MYPROXY_PASSWD_OTHER
    retrieve $MYPROXY_PASSWD_OTHER
    info

    change_passphrase $MYPROXY_PASSWD_OTHER $MYPROXY_PASSWD
    retrieve $MYPROXY_PASSWD
    info

    destroy
fi