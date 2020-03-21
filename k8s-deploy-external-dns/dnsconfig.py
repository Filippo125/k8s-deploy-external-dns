from provider import OVHProvider


class DNSConfig:

	def __init__(self, record, target, provider, config):
		if provider == "ovh":
			self.provider = OVHProvider(config_file=config)
		self.target = target
		self.record = record
		chunk = str(record).rsplit(".", maxsplit=2)
		if len(chunk) < 3:
			raise Exception("I'm able to deploy only subdomain")
		self.subdomain = chunk[0]
		self.zonename = ".".join(chunk[1:])

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
