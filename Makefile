SHELL=/bin/bash

#Confirm Ansible is Installed 
CHECK := $(shell command -v ansible-playbook 2> /dev/null)

#Set configuration and playbook definitions
export ANSIBLE_CONFIG := configuration/ansible/ansible.cfg
INVENTORY ?= configuration/ansible/inventory.yaml
PLAYBOOK ?= ansible/playbooks/main_playbook.yaml

.PHONY: build_runtime_environment, setup_docker_swarm, setup_cluster_environment, deploy_fedLearn_stack, destroy_fedLearn_environment, rebuild_runtime_containers, rebuild_model, update_fedLearn_configuration, scale_swarm

#Default Target, all
all:
ifndef CHECK
	$(Error: Ansible is not installed. Install Ansible with python3 -m pip install -U ansible)
endif
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t build_runtime_environment,setup_docker_swarm,setup_docker_registry,deploy_fedLearn_stack
 
build_runtime_environment:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t build_runtime_environment
 
setup_docker_swarm:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t setup_docker_swarm
 
setup_docker_registry:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t setup_docker_registry

deploy_fedLearn_stack:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t deploy_fedLearn_stack
 
destroy_docker_swarm:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t destroy_swarm_environment
 
rebuild_runtime_containers:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t build_runtime_environment,setup_docker_registry,deploy_fedLearn_stack --extra-vars "rebuild_containers=true container_redeploy=true"
 
rebuild_model:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t build_runtime_environment,setup_docker_registry,deploy_fedLearn_stack --extra-vars "rebuild_model=true container_redeploy=true"
 
update_fedLearn_configuration:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t build_runtime_environment,setup_docker_registry,deploy_fedLearn_stack --extra-vars "config_redeploy=true container_redeploy=true"
 
scale_swarm:
	ansible-playbook $(PLAYBOOK) -i $(INVENTORY) -t setup_docker_swarm,deploy_fedLearn_stack,destroy_swarm_environment --extra-vars "scale_down=true"
