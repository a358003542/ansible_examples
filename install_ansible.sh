#!/bin/bash
#
# THIS SCRIPT INSTALLS ANSIBLE
# DO NOT RUN IF ANSIBLE IS ALREADY INSTALLED ON YOUR SYSTEM


if ansible --version &> /dev/null ; then
  echo "Ansible is already installed."
  echo "Doing nothing."
  echo "Exiting now."
  exit 0
fi

if [[ $EUID -ne 0 ]]; then
    echo "You are NOT running this script as root."
    echo "You should."
    echo "Really."
    exit 1
fi


echo "Install ansible from web..."
if [[ ! -x $(which lsb_release 2>/dev/null) ]]; then

  if [[ -x $(which yum 2>/dev/null) ]]; then
  yum install -y redhat-lsb-core
  fi

  if [[ -x $(which apt 2>/dev/null) ]]; then
  apt install -y lsb-release
  fi
fi

# GET OS VENDOR
os_VENDOR=$(lsb_release -i -s)
# GET OS MAJOR VERSION
os_VERSION=$(lsb_release  -r  -s | cut -d. -f 1)

echo "*** Detected Linux $os_VENDOR $os_VERSION ***"

if [[ "Debian" =~ $os_VENDOR ]]; then
  apt-get update
  apt-get install -y python-pip python-dev git build-essential
  pip install PyYAML jinja2 paramiko
  git clone https://github.com/ansible/ansible.git
  cd ansible
  git submodule update --init --recursive
  make install
  mkdir /etc/ansible
elif [[ "Ubuntu" =~ $os_VENDOR || "LinuxMint" =~ $os_VENDOR ]]; then
  add-apt-repository -y ppa:ansible/ansible
  apt-get update
  apt-get install -y ansible
elif [[ "RedHatEnterpriseServer" =~ $os_VENDOR || "CentOS" =~ $os_VENDOR ]]; then
  if ( rpm -q epel-release &> /dev/null ); then
    echo "*** Installing Ansible from EPEL... ***"
    yum install -y ansible
  else
    echo "*** Installing EPEL... ***"
    yum install -y epel-release
    echo "*** Installing Ansible from EPEL... ***"
    yum install -y ansible
  fi
else
  echo "*** Unsupported platform ${os_VENDOR}: ${os_VERSION} ***"
  exit 1
fi



if ( ansible --version &> /dev/null ); then
echo "*** $(ansible --version | head -n1) installed successfully ***"
else
echo "Something went wrong, please have a look at the script output"
fi
