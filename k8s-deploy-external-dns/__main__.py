import logging
import sys
from datetime import datetime
import pytz
import argparse


from kubernetes import client, watch
from .dnsconfig import DNSConfig

logger = logging.getLogger('k8s_deploy_dns')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

parser = argparse.ArgumentParser()
parser.add_argument('--k8s-config-file', dest='k8s_config_file', metavar='S', type=str, help='Kubernetes configuration file')
parser.add_argument('--k8s-token', dest='k8s_token', metavar='S', type=str, help='Kubernetes serviceaccount token')
parser.add_argument('--k8s-host', dest='k8s_host', metavar='S', type=str, help='Kubernetes  API host')
parser.add_argument('--k8s-ssl-verify', dest='k8s_ssl_verify', metavar='B', default=True, type=bool, help='Kubernetes verify ssl')

parser.add_argument('--dns-provider', dest='dns_provider', metavar='S', type=str, help='External DNS provider')
parser.add_argument('--dns-config-file', dest='dns_config_file', metavar='S', type=str, help='DNS configuration file')

parser.add_argument('--dry-run', dest='dry_run', type=bool, nargs='?', default=False, help='Fake deploy dns')


args = parser.parse_args()

k8s_token = ""
k8s_host = ""


if args.k8s_config_file:
	with open(args.k8s_config_file, "r") as f:
		config = f.read().splitlines()
		k8s_token = config[0]
		k8s_host = config[1]
		k8s_ssl_verify = config[2] in ["True", "true", "1", "TRUE"]

if args.k8s_token:
	k8s_token = args.k8s_token
if args.k8s_host:
	k8s_host = args.k8s_host
k8s_ssl_verify = args.k8s_ssl_verify

# Create a configuration object
k8s_configuration = client.Configuration()
k8s_configuration.host = k8s_host
k8s_configuration.verify_ssl = k8s_ssl_verify
k8s_configuration.api_key = {"authorization": "Bearer " + k8s_token}

# Create a ApiClient with our config
api_client = client.ApiClient(k8s_configuration)

v1_extensions = client.ExtensionsV1beta1Api(api_client)

START_TIME = datetime.utcnow().replace(tzinfo=pytz.UTC)
logger.info("All events before %s will be ignored" % (START_TIME.strftime("%d/%m/%y %H:%M")))
DRY_RUN = args.dry_run
if DRY_RUN:
	logger.info("Dry Run mode activated, deploy on DNS")


def analyze_object(event_type,ob):
	if event_type == 'ADDED':
		creation_timestamp = ob.metadata.creation_timestamp
		if creation_timestamp < START_TIME:
			logger.debug("[ADDED]%s.%s before start time " % (ob.metadata.namespace, ob.metadata.name))
		else:
			logger.debug("[ADDED]%s.%s after start time " % (ob.metadata.namespace, ob.metadata.name))
			dnsConfigs = DNSConfig.build_from_ingress_rule(ob)
			for dnsConfig in dnsConfigs:
				print(dnsConfig)
				if not DRY_RUN:
					dnsConfig.deploy()
	elif event_type == 'MODIFIED':
		dnsConfigs = DNSConfig.build_from_ingress_rule(ob)
		for dnsConfig in dnsConfigs:
			print(dnsConfig)
			if not DRY_RUN:
				dnsConfig.deploy()
	elif event_type == 'DELETED':
		dnsConfigs = DNSConfig.build_from_ingress_rule(ob)
		for dnsConfig in dnsConfigs:
			print(dnsConfig)
			if not DRY_RUN:
				dnsConfig.delete()


stop = False
w = watch.Watch()
for event in w.stream(v1_extensions.list_namespaced_ingress, namespace="kube-system",):
	logger.info("[%s] %s" % (event['type'], event['object'].metadata.name))
	analyze_object(event['type'], event['object'])
	if stop:
		w.stop()
		exit()

exit()


