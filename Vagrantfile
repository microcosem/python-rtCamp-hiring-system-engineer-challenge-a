Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  #config.vm.provision "shell",
    #path: "provision/main.sh", args: "-d example.com",
    #upload_path: "/vagrant/provision/main.sh"
  config.vm.provider "virtualbox" do |v|
    v.name = "rtcamp-challenge-a"
  end
end
