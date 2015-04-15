#
# java alternatives for rhel, debian
#
define jdk7::config::alternatives(
  $java_home_dir  = undef,
  $full_version   = undef,
  $priority       = undef,
  $user           = undef,
  $group          = undef,
)
{
  case $::osfamily {
    'RedHat': {
      $alt_command = 'alternatives'
    }
    'Debian', 'Suse':{
      $alt_command = 'update-alternatives'
    }
    default: {
      fail("Unrecognized osfamily ${::osfamily}, please use it on a Linux host")
    }
  }

  exec { "java alternatives ${title}":
    command   => "${alt_command} --install /usr/bin/${title} ${title} ${java_home_dir}/${full_version}/bin/${title} ${priority}",
    unless    => "${alt_command} --display ${title} | /bin/grep ${full_version} | /bin/grep 'priority ${priority}$'",
    path      => '/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin',
    logoutput => true,
    user      => $user,
    group     => $group,
  }
}