import asyncio
from concurrent.futures import ProcessPoolExecutor

from cli_util import parse_cli, get_logger
from ingressrulewatcher import IngressRuleWatcher

from kubernetes import client
from kubernetes import config as k8s_config


from servicewatcher import ServiceWatcher


LOG_LEVEL = "DEBUG"

if __name__ == "__main__":
	args = parse_cli()
	logger = get_logger("main",LOG_LEVEL)
	k8s_token = None
	k8s_host = None
	k8s_ssl_verify = True

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
	if args.k8s_ssl_verify is not None:
		k8s_ssl_verify = args.k8s_ssl_verify

	if k8s_host is None or k8s_token is None:
		logger.info("Use Kubernetes in cluster configuration")
		k8s_config.load_incluster_config()
		api_client = client.ApiClient()
	else:
		# Create a configuration object
		k8s_configuration = client.Configuration()
		k8s_configuration.host = k8s_host
		k8s_configuration.verify_ssl = k8s_ssl_verify
		k8s_configuration.api_key = {"authorization": "Bearer " + k8s_token}
		# Create a ApiClient with custom config
		api_client = client.ApiClient(k8s_configuration)


	# Create DNS Config dictionary
	dns_config = {}
	dns_config[args.dns_provider] = args.dns_config_file

	ingress_rule_watcher = IngressRuleWatcher(dns_config=dns_config, api_client=api_client, logger=get_logger("ingress-rule-watcher", LOG_LEVEL), dry_run=args.dry_run)
	service_watcher = ServiceWatcher(dns_config=dns_config, api_client=api_client, logger=get_logger("service-watcher", LOG_LEVEL), dry_run=args.dry_run)

	loop = asyncio.get_event_loop()
	loop.run_in_executor(None, ingress_rule_watcher.run)
	loop.run_in_executor(None, service_watcher.run)

	loop.run_forever()

