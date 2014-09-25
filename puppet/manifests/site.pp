node 'soa2admin2.example.com','mft1admin.example.com' {

  include os
  include java
  include orawls::weblogic
  include orautils
  include fmw
  include opatch

  include domains,nodemanager,startwls,userconfig
  include machines,managed_servers,clusters
  include file_persistence
  include jms_servers
  include jms_modules
  include jms_module_subdeployments

  include fmw_cluster
  include fmw_jrf_cluster
  include fmw_log_dir
  include fmw_webtier

  Class['java'] -> Class['orawls::weblogic']

}

class os {

  $host_instances = hiera('hosts', {})
  create_resources('host',$host_instances)

  exec { "create swap file":
    command => "/bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=8192",
    creates => "/var/swap.1",
  }

  exec { "attach swap file":
    command => "/sbin/mkswap /var/swap.1 && /sbin/swapon /var/swap.1",
    require => Exec["create swap file"],
    unless => "/sbin/swapon -s | grep /var/swap.1",
  }

  #add swap file entry to fstab
  exec {"add swapfile entry to fstab":
    command => "/bin/echo >>/etc/fstab /var/swap.1 swap swap defaults 0 0",
    require => Exec["attach swap file"],
    user => root,
    unless => "/bin/grep '^/var/swap.1' /etc/fstab 2>/dev/null",
  }

  service { iptables:
        enable    => false,
        ensure    => false,
        hasstatus => true,
  }

  group { 'dba' :
    ensure => present,
  }

  # http://raftaman.net/?p=1311 for generating password
  # password = oracle
  user { 'oracle' :
    ensure     => present,
    groups     => 'dba',
    shell      => '/bin/bash',
    password   => '$1$DSJ51vh6$4XzzwyIOk6Bi/54kglGk3.',
    home       => "/home/oracle",
    comment    => 'oracle user created by Puppet',
    managehome => true,
    require    => Group['dba'],
  }

  $install = [ 'binutils.x86_64','unzip.x86_64',
               'xorg-x11-xauth.x86_64','compat-libcap1.x86_64',
               'compat-libstdc++-33.x86_64','libaio-devel.x86_64']


  package { $install:
    ensure  => present,
  }

  class { 'limits':
    config => {
               '*'       => {  'nofile'  => { soft => '2048'   , hard => '8192',   },},
               'oracle'  => {  'nofile'  => { soft => '65536'  , hard => '65536',  },
                               'nproc'   => { soft => '2048'   , hard => '16384',   },
                               'memlock' => { soft => '1048576', hard => '1048576',},
                               'stack'   => { soft => '10240'  ,},},
               },
    use_hiera => false,
  }

  sysctl { 'kernel.msgmnb':                 ensure => 'present', permanent => 'yes', value => '65536',}
  sysctl { 'kernel.msgmax':                 ensure => 'present', permanent => 'yes', value => '65536',}
  sysctl { 'kernel.shmmax':                 ensure => 'present', permanent => 'yes', value => '2588483584',}
  sysctl { 'kernel.shmall':                 ensure => 'present', permanent => 'yes', value => '2097152',}
  sysctl { 'fs.file-max':                   ensure => 'present', permanent => 'yes', value => '6815744',}
  sysctl { 'net.ipv4.tcp_keepalive_time':   ensure => 'present', permanent => 'yes', value => '1800',}
  sysctl { 'net.ipv4.tcp_keepalive_intvl':  ensure => 'present', permanent => 'yes', value => '30',}
  sysctl { 'net.ipv4.tcp_keepalive_probes': ensure => 'present', permanent => 'yes', value => '5',}
  sysctl { 'net.ipv4.tcp_fin_timeout':      ensure => 'present', permanent => 'yes', value => '30',}
  sysctl { 'kernel.shmmni':                 ensure => 'present', permanent => 'yes', value => '4096', }
  sysctl { 'fs.aio-max-nr':                 ensure => 'present', permanent => 'yes', value => '1048576',}
  sysctl { 'kernel.sem':                    ensure => 'present', permanent => 'yes', value => '250 32000 100 128',}
  sysctl { 'net.ipv4.ip_local_port_range':  ensure => 'present', permanent => 'yes', value => '9000 65500',}
  sysctl { 'net.core.rmem_default':         ensure => 'present', permanent => 'yes', value => '262144',}
  sysctl { 'net.core.rmem_max':             ensure => 'present', permanent => 'yes', value => '4194304', }
  sysctl { 'net.core.wmem_default':         ensure => 'present', permanent => 'yes', value => '262144',}
  sysctl { 'net.core.wmem_max':             ensure => 'present', permanent => 'yes', value => '1048576',}

}

class java {
  require os

  $remove = ["java-1.7.0-openjdk.x86_64",
             "java-1.6.0-openjdk.x86_64" ]

  package { $remove:
    ensure  => absent,
  }

  include jdk7

  jdk7::install7{ 'jdk1.7.0_55':
      version                   => "7u55" ,
      fullVersion               => "jdk1.7.0_55",
      alternativesPriority      => 18000,
      x64                       => true,
      downloadDir               => "/var/tmp/install",
      urandomJavaFix            => true,
      rsakeySizeFix             => true,
      cryptographyExtensionFile => "UnlimitedJCEPolicyJDK7.zip",
      sourcePath                => "/software",
  }

}

class fmw{
  require os,java,orawls::weblogic

  if ( defined(Orawls::Fmw["b2b1213"])) {
    Orawls::Fmw["soa1213"] -> Orawls::Fmw["b2b1213"]
  }

  $default_params = {}
  $fmw_installations = hiera('fmw_installations', {})
  create_resources('orawls::fmw',$fmw_installations, $default_params)
}

class opatch{
  require fmw,orawls::weblogic
  $default_params = {}
  $opatch_instances = hiera('opatch_instances', {})
  create_resources('orawls::opatch',$opatch_instances, $default_params)
}

class rcu{
  require fmw,orawls::weblogic,opatch
  $default_params = {}
  $rcu_instances = hiera('rcu_instances', {})
  create_resources('orawls::utils::rcu',$rcu_instances, $default_params)
}

class domains{
  require orawls::weblogic,opatch,rcu

  $default_params = {}
  $domain_instances = hiera('domain_instances', {})
  create_resources('orawls::domain',$domain_instances, $default_params)

  $domain_address = hiera('domain_adminserver_address')
  $domain_port    = hiera('domain_adminserver_port')

  $str_version  = hiera('wls_version')
  $domains_path = hiera('wls_domains_dir')
  $domain_name  = hiera('domain_name')

  orautils::nodemanagerautostart{"autostart weblogic":
    version     => "${str_version}",
    domain      => $domain_name,
    domainPath  => "${domains_path}/${domain_name}",
    wlHome      => hiera('wls_weblogic_home_dir'),
    user        => hiera('wls_os_user'),
    jsseEnabled => true,
  }

  wls_setting { 'default':
    user               => hiera('wls_version'),
    weblogic_home_dir  => hiera('wls_weblogic_home_dir'),
    connect_url        => "t3://${domain_address}:${domain_port}",
    weblogic_user      => hiera('wls_weblogic_user'),
    weblogic_password  => hiera('domain_wls_password'),
  }

}

class nodemanager {
  require orawls::weblogic, domains
  $default_params = {}
  $nodemanager_instances = hiera('nodemanager_instances', {})
  create_resources('orawls::nodemanager',$nodemanager_instances, $default_params)
}

class startwls {
  require orawls::weblogic, domains,nodemanager
  $default_params = {}
  $control_instances = hiera('control_instances', {})
  create_resources('orawls::control',$control_instances, $default_params)
}

class userconfig{
  require orawls::weblogic, domains, nodemanager, startwls
  $default_params = {}
  $userconfig_instances = hiera('userconfig_instances', {})
  create_resources('orawls::storeuserconfig',$userconfig_instances, $default_params)
}

class machines{
  require userconfig
  $default_params = {}
  $machines_instances = hiera('machines_instances', {})
  create_resources('wls_machine',$machines_instances, $default_params)
}

class managed_servers{
  require machines
  $default_params = {}
  $managed_servers_instances = hiera('managed_servers_instances', {})
  create_resources('wls_server',$managed_servers_instances, $default_params)
}

class clusters{
  require managed_servers
  $default_params = {}
  $cluster_instances = hiera('cluster_instances', {})
  create_resources('wls_cluster',$cluster_instances, $default_params)
}

class fmw_cluster{
  require clusters
  $default_params = {}
  $fmw_cluster_instances = hiera('fmw_cluster_instances', $default_params)
  create_resources('orawls::utils::fmwcluster',$fmw_cluster_instances, $default_params)
}

class fmw_jrf_cluster{
  require fmw_cluster
  $default_params = {}
  $fmw_jrf_cluster_instances = hiera('fmw_jrf_cluster_instances', $default_params)
  create_resources('orawls::utils::fmwclusterjrf',$fmw_jrf_cluster_instances, $default_params)
}

class fmw_log_dir {
  require fmw_jrf_cluster
  $default_params = {}
  $fmwlogdir_instances = hiera('fmwlogdir_instances', {})
  create_resources('orawls::fmwlogdir',$fmwlogdir_instances, $default_params)
}

class fmw_webtier {
  require fmw_log_dir
  $default_params = {}
  $webtier_instances = hiera('webtier_instances', {})
  create_resources('orawls::utils::webtier',$webtier_instances, $default_params)
}

class file_persistence_folders{
  require fmw_webtier
  $default_params = {}
  $file_persistence_folders = hiera('file_persistence_folders', {})
  create_resources('file',$file_persistence_folders, $default_params)
}

class file_persistence{
  require file_persistence_folders
  $default_params = {}
  $file_persistence = hiera('file_persistence_store_instances', {})
  create_resources('wls_file_persistence_store',$file_persistence, $default_params)
}

class jms_servers{
  require file_persistence
  $default_params = {}
  $jms_servers_instances = hiera('jmsserver_instances', {})
  create_resources('wls_jmsserver',$jms_servers_instances, $default_params)
}

class jms_modules{
  require jms_servers
  $default_params = {}
  $jms_modules_instances = hiera('jms_modules_instances', {})
  create_resources('wls_jms_module',$jms_modules_instances, $default_params)
}

class jms_module_subdeployments{
  require jms_modules
  $default_params = {}
  $jms_subdeployments_instances = hiera('jms_subdeployments_instances', {})
  create_resources('wls_jms_subdeployment',$jms_subdeployments_instances, $default_params)
}
