import argparse
import logging
import sys


def get_logger(name,level):
	logger = logging.getLogger(name)
	handler = logging.StreamHandler(sys.stdout)
	if level == "DEBUG":
		logger.setLevel(logging.DEBUG)
		handler.setLevel(logging.DEBUG)
	elif level == "WARNING":
		logger.setLevel(logging.WARNING)
		handler.setLevel(logging.WARNING)
	elif level == "ERROR":
		logger.setLevel(logging.ERROR)
		handler.setLevel(logging.ERROR)
	else:
		logger.setLevel(logging.INFO)
		handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger

def parse_cli():
	parser = argparse.ArgumentParser()
	parser.add_argument('--k8s-config-file', dest='k8s_config_file', metavar='S', type=str,
	                    help='Kubernetes configuration file')
	parser.add_argument('--k8s-token', dest='k8s_token', metavar='S', type=str, help='Kubernetes serviceaccount token')
	parser.add_argument('--k8s-host', dest='k8s_host', metavar='S', type=str, help='Kubernetes  API host')
	parser.add_argument('--k8s-ssl-verify', dest='k8s_ssl_verify', metavar='B', default=None, type=bool,
	                    help='Kubernetes verify ssl')

	parser.add_argument('--dns-provider', dest='dns_provider', metavar='S', type=str, help='External DNS provider')
	parser.add_argument('--dns-config-file', dest='dns_config_file', metavar='S', type=str, help='DNS configuration file')

	parser.add_argument('--dry-run', dest='dry_run', type=bool, nargs='?', default=False, help='Fake deploy dns')

	args = parser.parse_args()
	return args