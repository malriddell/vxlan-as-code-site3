
mkdir vxlan-as-code-site3
cd vxlan-as-code-site3

git clone https://github.com/netascode/ansible-dc-vxlan-example.git .

rm -rf .git

git init --initial-branch=main

mkdir -p collections/ansible_collections/cisco

pyenv virtualenv 3.12.10 sac-site3
pyenv local sac-site3

pip install --upgrade pip
pip install -r requirements.txt

ansible-galaxy collection install -p collections/ansible_collections/ -r requirements.yaml
ansible-galaxy collection install -p collections/ansible_collections/ git+https://github.com/CiscoDevNet/ansible-dcnm.git,develop
ansible-galaxy collection install  git+https://github.com/CiscoDevNet/ansible-dcnm.git,develop

ansible-galaxy collection install -p collections/ansible_collections/  git+https://github.com/malriddell/ansible-dc-vxlan,issue-662




cat << EOF >> ansible.cfg
[defaults]
collections_path = $PYENV_VIRTUAL_ENV/lib/python3.10/site-packages/ansible/collections:./collections/ansible_collections/

# callback_whitelist=ansible.posix.timer,ansible.posix.profile_tasks,ansible.posix.profile_roles
# callbacks_enabled=ansible.posix.timer,ansible.posix.profile_tasks,ansible.posix.profile_roles
# stdout_callback = community.general.yaml
# bin_ansible_callbacks = True
EOF

ln -s ../nac-vxlan/schemas/schema.yaml ./schema/
ln -s ../nac-vxlan/templates/nd/tests tests/templates
ln -s ../nac-vxlan/jinja_filters  tests/jinja_filters
