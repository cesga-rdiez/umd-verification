function get_umd_release {
    # $1 - UMD/CMD distribution: umd3,umd4,cmd1 

    # UMD or CMD
    case $1 in
        UMD3) release_str="umd_release=3" ;;
        UMD4) release_str="umd_release=4" ;;
        CMD1) release_str="cmd_release=1,openstack_release=mitaka" ;;
        *) echo "UMD distribution '$distro' not known" && exit -1
    esac

    echo $release_str
}


function get_sudo_type {
    # $1 - Operating system: sl6, (others)

    [[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo
    
    echo $sudocmd
}


function get_repos {
    # $1 - Comma-separated string with the repository URLs
    # $2 - Argument name (prefix)
    
    #prefix=$1
    #shift
    prefix=repository_file
    
    c=0
    repostr=''
    for i in "$@"; do
        c=$((c+1))
        [ -n "$repostr" ] && repostr=$repostr','
        repostr=$repostr"${prefix}_$c=$i"
    done
    
    echo $repostr
}


function deploy_config_management {
    # $1 - config management tool: ansible, puppet
    # $2 - sudo type
    # $3 - module URL

    sudocmd=$2
    module_url=$3
    module_name="`basename $3`"
    ## ansible OR puppet
    case $1 in
        *ansible*)
            $sudocmd pip install ansible==2.2
            module_path=/tmp/$module_name
            $sudocmd rm -rf $module_path
            git clone $module_url $module_path
            $sudocmd ansible-galaxy install -r ${module_path}/requirements.yml
            ;;
        *puppet*)
            if [[ $OS == sl6* ]] ; then 
                $sudocmd /usr/local/rvm/rubies/ruby-1.9.3-p551/bin/gem install librarian-puppet
                $sudocmd sed -i '/secure_path =/ s/$/:\/usr\/local\/rvm\/gems\/ruby-1.9.3-p551\/bin/' /etc/sudoers
            fi
            ;;
        *)
            echo "Configuration management tool '$1' not supported" && exit -1
            ;;
    esac
}

function add_hostname_as_localhost {
    # $1 - sudo type

    $1 sed -i "/^127\.0\.0\.1/ s/$/ `hostname`/" /etc/hosts
}
