is_installed() {
    [ -z "$(dpkg -l | awk "/^ii  $1/")" ]
}

# is_running_as_root() {
#     [ "$EUID" -ne 0 ]
# }

# if is_running_as_root; then
#     echo "Please run as root"
#     exit
#   fi

if is_installed "filebeat"; then
  echo 'filebeat is not installed...'
  echo 'Installing filebeat...'
  wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
  apt-get install apt-transport-https
  echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-8.x.list
  apt-get update
  apt-get install filebeat
  echo 'filebeat is installed, Configuring...'
  cp .filebeat/filebeat.yml /etc/filebeat/filebeat.yml
fi

echo 'Running filebeat...'
nohup filebeat -e -strict.perms=false >/dev/null 2>&1 &
