#!/usr/bin/python

import subprocess
import docker
client = docker.from_env()

if (len(sys.argv) > 1):
	postfix = sys.argv[0]
	print("Images will be postfixed by " + postfix)
else:
	postfix = ""

def update_replicas(service, replicas):
	param = service.name + "=" + str(replicas)
	subprocess.run(["docker", "service", "scale", param])

def create_service(name, replicas, postfix):
	if replicas > 0:
		subprocess.run(["bash", "docker_service.sh", "-r", str(replicas), "create_service_" + name, postfix])

def create(name):
	subprocess.run(["bash", "docker_service.sh", "create_" + name])

def get_service(name):
	services = client.services.list()
	for service in services:
		if service.name == name:
			return service
	return None

def create_or_update_service(name, replicas, postfix):
	service = get_service(name)
	if service is not None:
		update_replicas(service, replicas)
	else:
		create_service(name, replicas, postfix)

def create_network():
	client.networks.create("smart-meter-net", driver="overlay")

def run_scenario(steps):
	for step in steps:
		if step[0] == "create_service" :
			create_or_update_service(step[1], step[2], postfix)
		else:
			create(step[1])

create_network = ["create", "network"]
create_service_cassandra = ["create_service", "cassandra", 1]
create_service_spark_master = ["create_service", "spark-master", 1]
create_service_spark_slave = ["create_service", "spark-slave", 2]
create_service_nats = ["create_service", "nats", 1]
create_service_app_streaming = ["create_service", "app-streaming", 1]
create_service_monitor = ["create_service", "monitor", 1]
create_service_reporter = ["create_service", "reporter", 1]
create_cassandra_tables = ["create", "cassandra_tables", 1]
create_service_cassandra_inject = ["create_service", "cassandra-inject", 1]
create_service_inject = ["create_service", "inject", 1]

stop_service_cassandra = ["create_service", "cassandra", 0]
stop_service_spark_master = ["create_service", "spark-master", 0]
stop_service_spark_slave = ["create_service", "spark-slave", 0]
stop_service_nats = ["create_service", "nats", 0]
stop_service_app_streaming = ["create_service", "app-streaming", 0]
stop_service_monitor = ["create_service", "monitor", 0]
stop_service_reporter = ["create_service", "reporter", 0]
stop_service_cassandra_inject = ["create_service", "cassandra-inject", 0]
stop_service_inject = ["create_service", "inject", 0]

all_steps = [
	create_network,
	create_service_cassandra,
	create_service_spark_master,
	create_service_spark_slave,
	create_service_nats,
	create_service_app_streaming,
	create_service_monitor,
	create_service_reporter,
	create_cassandra_tables,
	create_service_cassandra_inject,
	create_service_inject
	]

def run_or_kill_scenario(steps):
	# Collect all existing services names
	all_remaining_services = []
	for step in all_steps:
		if step[0] == "create_service" :
			all_remaining_services.append(step[1])
	# Remove all requested services
	for step in steps:
		if step[0] == "create_service" :
			all_remaining_services.remove(step[1])
	#
	print("All of those services will be desactivated: " + str(all_remaining_services))
	for name in all_remaining_services:
		create_or_update_service(name, 0, postfix)
	# Finaly, run the requested scenario
	run_scenario(steps)

def run_all_steps():
	run_scenario(all_steps)

def run_inject_raw_data_into_cassandra():
	run_or_kill_scenario([
		create_network,
		create_service_cassandra,
		create_service_nats,
		create_cassandra_tables,
		create_service_cassandra_inject,
		create_service_inject
		])