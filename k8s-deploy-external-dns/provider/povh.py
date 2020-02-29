import ovh


class OVHProvider:
	DEFAULT_TTL = 60
	def __init__(self, config_file="ovh.key"):
		self.client = ovh.Client(config_file=config_file)

	def _get_record_id(self,zonename,subdomain):
		response = self.client.get("/domain/zone/%s/record" % zonename, subDomain=subdomain, fieldType="A")
		if len(response) == 1:
			return response[0]
		elif len(response) == 0:
			return None
		raise Exception("Found more than one record for %s in %s type A" % (subdomain, zonename))

	def get_record(self, zonename, subdomain):
		record_id = self._get_record_id(zonename=zonename, subdomain=subdomain)
		if record_id:
			record = self.client.get("/domain/zone/%s/record/%d" % (zonename, record_id))
			return record
		return None

	def get_domains_zone(self, zonename):
		response = self.client.get("/domain/zone/%s/record" % zonename)
		return response

	def create_record(self, zonename, subdomain, target):
		result = self.client.post('/domain/zone/%s/record' % zonename, fieldType="A", subDomain=subdomain, target=target, ttl=self.DEFAULT_TTL)
		if result:
			self._refresh_zone(zonename=zonename)
			return True
		else:
			raise Exception(result)

	def update_record(self, record, target):
		result = self.client.put('/domain/zone/%s/record/%d' % (record["zone"], record["id"]), target=target)
		self._refresh_zone(zonename=record["zone"])
		return True

	def delete_record(self, zonename, subdomain):
		record_id = self._get_record_id(zonename=zonename, subdomain=subdomain)
		if record_id:
			self.client.delete('/domain/zone/%s/record/%d' % (zonename, record_id))
			self._refresh_zone(zonename=zonename)
		return None

	def _refresh_zone(self, zonename):
		result = self.client.post('/domain/zone/%s/refresh' % zonename)
		return result

	def is_record_already_deployed(self,zonename, subdomain, target):
		record = self.get_record(zonename=zonename,subdomain=subdomain)
		if record:
			return record["id"] == target
		return False

	def deploy_record(self,zonename, subdomain, target):
		record = self.get_record(zonename=zonename, subdomain=subdomain)
		if record and record["id"] == target:
			# nothing to do
			return True
		elif record:
			# update
			self.update_record(record=record,target=target)
		else:
			# new record
			self.create_record(zonename=zonename,subdomain=subdomain,target=target)
		return True