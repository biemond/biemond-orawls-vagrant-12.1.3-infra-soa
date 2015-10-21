require 'spec_helper'

describe 'jdk7::install7' , :type => :define do

  describe "Windows" do
    let(:facts) {{ :kernel          => 'Windows',
                   :operatingsystem => 'Windows',
                   :osfamily        => 'Windows'}}
    let(:title) {'JDK7'}
    let(:params){{:download_dir     => '/install',
                }}
    it do
      expect { should contain_exec("create /install directory")
             }.to raise_error(Puppet::Error, /Unrecognized operating system Windows, please use it on a Linux host/)
    end
  end
  describe "SunOS" do
    let(:facts) {{ :kernel          => 'SunOS',
                   :operatingsystem => 'Solaris',
                   :osfamily        => 'Solaris'}}
    let(:title) {'JDK7'}
    let(:params){{:download_dir     => '/install',
                }}
    it do
      expect { should contain_exec("create /install directory")
             }.to raise_error(Puppet::Error, /Unrecognized operating system SunOS, please use it on a Linux host/)
    end
  end

  describe "CentOS with all the defaults" do
    let(:facts) {{ :operatingsystem => 'CentOS' ,
                   :kernel          => 'Linux',
                   :osfamily        => 'RedHat' }}
    let(:title) {'JDK7'}

    describe "on operatingsystem CentOS" do
      it do
        should contain_exec("create /install directory").with({
            'command' => "mkdir -p /install",
            'unless'  => "test -d /install",
            'user'    => 'root',
          })
      end
      it do
        should contain_file("/install").with({
            'ensure'     => 'directory',
            'replace'    => false,
            'owner'      => 'root',
            'group'      => 'root',
            'mode'       => '0777',
          }).that_requires('Exec[create /install directory]')
      end
      it do
        should contain_file("/install/jdk-7u79-linux-x64.tar.gz").with({
            'ensure'     => 'file',
            'source'     => "puppet:///modules/jdk7//jdk-7u79-linux-x64.tar.gz",
            'replace'    => false,
            'owner'      => 'root',
            'group'      => 'root',
            'mode'       => '0777',
          }).that_requires('File[/install]')
      end

      it do
        should contain_jdk7__config__javaexec("jdkexec JDK7 7u79").with({
            'download_dir'                => '/install',
            'full_version'                => 'jdk1.7.0_79',
            'java_homes_dir'              => '/usr/java',
            'jdk_file'                    => 'jdk-7u79-linux-x64.tar.gz',
            'cryptography_extension_file' => nil,
            'alternatives_priority'       => '17065',
            'user'                        => 'root',
            'group'                       => 'root',
           }).that_requires("File[/install/jdk-7u79-linux-x64.tar.gz]")
      end
      it do
        should contain_exec("set urandom jdk1.7.0_79").with({
            'command' => "sed -i -e's/^securerandom.source=.*/securerandom.source=file:\\/dev\\/.\\/urandom/g' /usr/java/jdk1.7.0_79/jre/lib/security/java.security",
            'unless'  => "grep '^securerandom.source=file:/dev/./urandom' /usr/java/jdk1.7.0_79/jre/lib/security/java.security",
            'user'    => 'root',
          })
      end

    end

  end

  describe "RedHat with other default" do
    let(:facts) {{ :operatingsystem => 'RedHat' ,
                   :kernel          => 'Linux',
                   :osfamily        => 'RedHat' }}
    let(:title) {'JDK7'}
    let(:params){{:version                     => '7u51',
                  :full_version                => 'jdk1.7.0_51',
                  :java_homes                  => '/usr/java',
                  :x64                         => false,
                  :alternatives_priority       => 18000,
                  :download_dir                => '/tmp/install',
                  :cryptography_extension_file => 'UnlimitedJCEPolicyJDK7.zip',
                  :urandom_java_fix            => false,
                  :rsa_key_size_fix            => true,
                  :source_path                 => '/software',
                }}

    describe "on operatingsystem RedHat" do
      it do
        should contain_exec("create /tmp/install directory").with({
            'command' => "mkdir -p /tmp/install",
            'unless'  => "test -d /tmp/install",
            'user'    => 'root',
          })
      end
      it do
        should contain_file("/tmp/install").with({
            'ensure'     => 'directory',
            'replace'    => false,
            'owner'      => 'root',
            'group'      => 'root',
            'mode'       => '0777',
          }).that_requires('Exec[create /tmp/install directory]')
      end
      it do
        should contain_file("/tmp/install/jdk-7u51-linux-i586.tar.gz").with({
            'ensure'     => 'file',
            'source'     => "/software/jdk-7u51-linux-i586.tar.gz",
            'replace'    => false,
            'owner'      => 'root',
            'group'      => 'root',
            'mode'       => '0777',
          }).that_requires('File[/tmp/install]')
      end

      it do
        should contain_jdk7__config__javaexec("jdkexec JDK7 7u51").with({
            'download_dir'                => '/tmp/install',
            'full_version'                => 'jdk1.7.0_51',
            'java_homes_dir'              => '/usr/java',
            'jdk_file'                    => 'jdk-7u51-linux-i586.tar.gz',
            'cryptography_extension_file' => 'UnlimitedJCEPolicyJDK7.zip',
            'alternatives_priority'       => '18000',
            'user'                        => 'root',
            'group'                       => 'root',
           }).that_requires("File[/tmp/install/jdk-7u51-linux-i586.tar.gz]")
      end

      it do
        should contain_file("/tmp/install/UnlimitedJCEPolicyJDK7.zip").with({
            'ensure'     => 'file',
            'source'     => "/software/UnlimitedJCEPolicyJDK7.zip",
            'replace'    => false,
            'owner'      => 'root',
            'group'      => 'root',
            'mode'       => '0777',
          }).that_requires('File[/tmp/install]').that_comes_before('File[/tmp/install/jdk-7u51-linux-i586.tar.gz]')
      end

      it do
        should contain_exec("sleep 3 sec for urandomJavaFix jdk1.7.0_51").with({
            'command' => "/bin/sleep 3",
            'unless'  => "grep 'RSA keySize < 512' /usr/java/jdk1.7.0_51/jre/lib/security/java.security",
            'user'    => 'root',
          })#.that_requires('jdk7_config_javaexec[jdkexec JDK7 7u51]')
      end

      it do
        should contain_exec("set RSA keySize jdk1.7.0_51").with({
            'command'     => "sed -i -e's/RSA keySize < 1024/RSA keySize < 512/g' /usr/java/jdk1.7.0_51/jre/lib/security/java.security",
            'unless'      => "grep 'RSA keySize < 512' /usr/java/jdk1.7.0_51/jre/lib/security/java.security",
            'user'        => 'root',
            'refreshonly' => 'true',
          }).that_subscribes_to('Exec[sleep 3 sec for urandomJavaFix jdk1.7.0_51]')
      end

    end
  end

end
