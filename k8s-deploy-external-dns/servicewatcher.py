import logging
import sys
from datetime import datetime
from dnsconfig import DNSConfig
import pytz
from kubernetes import client, watch

class ServiceWatcher:

	def __init__(self,api_client,**kwargs):
		self.v1_api = client.CoreV1Api(api_client)
		if "logger" in kwargs:
			self.logger = kwargs.get("logger")
		else:
			logger = logging.getLogger('k8s_services_watcher')
			logger.setLevel(logging.DEBUG)
			handler = logging.StreamHandler(sys.stdout)
			handler.setLevel(logging.DEBUG)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.logger = logger
		self.dry_run = kwargs.get("dry_run", False)
		if self.dry_run:
			self.logger.info("Dry Run mode activated, deploy on DNS")
		self.start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
		self.logger.info("All events before %s will be ignored" % (self.start_time.strftime("%d/%m/%y %H:%M")))
		self.stop = False

	def run(self):
		self.logger.debug("Call run method")
		w = watch.Watch()
		for event in w.stream(self.v1_api.list_service_for_all_namespaces,):
			try:
				self.logger.info("[%s] %s" % (event['type'], event['object'].metadata.name))
				self._analyze_object(event['type'], event['object'])
				if self.stop:
					w.stop()
					self.logger.debug("Exit")
					return
			except Exception as e:
				self.logger.error("[%s] %s - %s"% (event['type'], event['object'].metadata.name, e))

	def _analyze_object(self, event_type, ob):
		if event_type == 'ADDED':
			creation_timestamp = ob.metadata.creation_timestamp
			if creation_timestamp < self.start_time:
				self.logger.debug("[ADDED] %s.%s before start time " % (ob.metadata.namespace, ob.metadata.name))
			else:
				self.logger.debug("[ADDED] %s.%s after start time " % (ob.metadata.namespace, ob.metadata.name))
				dnsConfigs = self._build_dns_config_list(ob)
				for dnsConfig in dnsConfigs:
					if not self.dry_run:
						dnsConfig.deploy()
		elif event_type == 'MODIFIED':
			dnsConfigs = self._build_dns_config_list(ob)
			for dnsConfig in dnsConfigs:
				if not self.dry_run:
					dnsConfig.deploy()
		elif event_type == 'DELETED':
			dnsConfigs = self._build_dns_config_list(ob)
			for dnsConfig in dnsConfigs:
				if not self.dry_run:
					dnsConfig.delete()

	@staticmethod
	def _build_dns_config_list(service) -> list:
		auto_deploy = service.metadata.annotations.get("dns-autodeploy")
		if auto_deploy not in [True, "true", "True", "yes", "1", 1]:
			return []
		if service.spec.type == "LoadBalancer":
			target = service.status.load_balancer.ingress[0].ip
		else:
			return []
		provider = service.metadata.annotations.get("dns-provider")
		fqdn = service.metadata.annotations.get("dns-fqdn")
		dns_config_list = []
		dns_config = DNSConfig(target=target, provider=provider, record=fqdn)
		dns_config_list.append(dns_config)
		return dns_config_list