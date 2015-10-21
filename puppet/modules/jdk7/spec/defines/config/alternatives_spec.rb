require 'spec_helper'

describe 'jdk7::config::alternatives' , :type => :define do


  describe "CentOS with all the defaults" do
    let(:facts) {{ :operatingsystem => 'CentOS' ,
                   :kernel          => 'Linux',
                   :osfamily        => 'RedHat' }}
    let(:title) {'java'}
    let(:params){{:java_home_dir       => '/usr/java',
                  :full_version        => 'jdk1.7.0_51',
                  :priority            => 18000,
                  :user                => 'root',
                  :group               => 'root',
                }}

    describe "on operatingsystem Redhat" do
      it do
        should contain_exec("java alternatives java").with({
            'command' => "alternatives --install /usr/bin/java java /usr/java/jdk1.7.0_51/bin/java 18000",
            'unless'  => "alternatives --display java | /bin/grep jdk1.7.0_51 | /bin/grep 'priority 18000$'",
            'user'    => 'root',
          })
      end

    end

  end

  describe "Debian" do
    let(:facts) {{ :operatingsystem => 'Debian' ,
                   :kernel          => 'Linux',
                   :osfamily        => 'Debian' }}
    let(:title) {'java'}
    let(:params){{:java_home_dir       => '/usr/java/jdk1.7.0_51',
                  :full_version        => 'jdk1.7.0_51',
                  :priority            => 18000,
                  :user                => 'root',
                  :group               => 'root',
                }}

    describe "on operatingsystem Debian" do
      it do
        should contain_exec("java alternatives java").with({
            'command' => "update-alternatives --install /usr/bin/java java /usr/java/jdk1.7.0_51/jdk1.7.0_51/bin/java 18000",
            'unless'  => "update-alternatives --display java | /bin/grep jdk1.7.0_51 | /bin/grep 'priority 18000$'",
            'user'    => 'root',
          })
      end

    end
  end

end
