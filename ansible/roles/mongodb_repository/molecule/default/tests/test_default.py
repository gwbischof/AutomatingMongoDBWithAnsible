import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def include_vars(host):
    ansible = host.ansible('include_vars',
                           'file="../../defaults/main.yml"',
                           False,
                           False)
    return ansible


def get_mongodb_version(host):
    return include_vars(host)['ansible_facts']['mongodb_version']


def test_redhat_mongodb_repository_file(host):
    # with capsys.disabled(): #Disable autocapture of output and send to stdout N.B capsys must be passed into function
    # print(include_vars(host)['ansible_facts'])
    mongodb_version = get_mongodb_version(host)
    if host.system_info.distribution == "redhat" \
            or host.system_info.distribution == "centos":
        f = host.file("/etc/yum.repos.d/mongodb-org-{0}.repo".format(mongodb_version))
        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        assert f.mode == 0o644
        assert f.md5sum == "8e09a9eaf2bebcb24f417ab86235bf70"


def test_redhat_yum_search(host):
    mongodb_version = get_mongodb_version(host)
    if host.system_info.distribution == "redhat" \
            or host.system_info.distribution == "centos":
        cmd = host.run("yum search mongodb-org --disablerepo='*' \
                            --enablerepo='mongodb-org-{0}'".format(mongodb_version))

        assert cmd.rc == 0
        assert "mongodb-org.x86_64" in cmd.stdout
        assert "mongodb-org-mongos.x86_64" in cmd.stdout
        assert "mongodb-org-server.x86_64" in cmd.stdout
        assert "mongodb-org-shell.x86_64" in cmd.stdout
        assert "mongodb-org-tools.x86_64" in cmd.stdout


def test_debian_mongodb_repository_file(host):
    mongodb_version = get_mongodb_version(host)
    if host.system_info.distribution == "debian" \
            or host.system_info.distribution == "ubuntu":
        f = host.file("/etc/apt/sources.list.d/mongodb-org-{0}.list".format(mongodb_version))

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'
        assert f.mode == 0o644
        if host.system_info.distribution == "debian":
            assert f.content_string.strip() == "deb http://repo.mongodb.org/apt/debian {0}/mongodb-org/{1} main".format(host.system_info.codename,
                                                                                                                        mongodb_version)
        else:
            assert f.content_string.strip() == "deb http://repo.mongodb.org/apt/ubuntu {0}/mongodb-org/{1} multiverse".format(host.system_info.codename,
                                                                                                                              mongodb_version)


def test_debian_apt_search(host):
    if host.system_info.distribution == "debian" \
            or host.system_info.distribution == "ubuntu":
        cmd = host.run("apt search mongodb-org")

        assert cmd.rc == 0
        assert "mongodb-org/" in cmd.stdout
        assert "mongodb-org-mongos/" in cmd.stdout
        assert "mongodb-org-server/" in cmd.stdout
        assert "mongodb-org-shell/" in cmd.stdout
        assert "mongodb-org-tools/" in cmd.stdout
