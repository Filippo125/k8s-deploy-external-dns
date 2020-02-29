from .provider import OVHProvider


class DNSConfig:

	def __init__(self, record, target, provider):
		if provider == "ovh":
			self.provider = OVHProvider(config_file="ovh.key")
		self.target = target
		self.record = record
		chunk = str(record).rsplit(".", maxsplit=2)
		if len(chunk) < 3:
			raise Exception("I'm able to deply only subdomain")
		self.subdomain = chunk[0]
		self.zonename = ".".join(chunk[1:])

	@staticmethod
	def build_from_ingress_rule(ingress_rule)->list:
		auto_deploy = ingress_rule.metadata.annotations.get("dns-autodeploy")
		if auto_deploy not in [True,"true","True","yes", "1", 1]:
			return []
		target = ingress_rule.metadata.annotations.get("dns-target")
		provider = ingress_rule.metadata.annotations.get("dns-provider")
		dns_config_list = []
		rules = ingress_rule.spec.rules
		for rule in rules:
			dns_config = DNSConfig(target=target, provider=provider, record=rule.host)
			dns_config_list.append(dns_config)
		return dns_config_list

	def deploy(self):
		self.provider.deploy_record(zonename=self.zonename, subdomain=self.subdomain, target=self.target)

	def delete(self):
		self.provider.delete_record(zonename=self.zonename, subdomain=self.subdomain)

	def __str__(self):
		return "DNSConfig{record=%s,target=%s,provider=%s}" % (self.record,self.target,self.provider)

	def __unicode__(self):
		return self.__str__()

	def __repr__(self):
		return self.__str__()
