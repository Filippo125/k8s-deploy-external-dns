# Kubernetes deployer on external dns
This tool watch services and ingress rule and create dns record on external dns provider
## Getting Started
These instructions will help you to deploy it on a live kubernetes cluster

### Prerequisites
* Kubernetes cluster (sure?)
* ServiceAccount with ingress and services read permissions (Above the section to create it)
* DNS zone in supported provider, currently only OVH is supported
### Create ServiceAccount
In your kubernetes cluster run:

1. Create ServiceAccount
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/001_service_account.yaml
```

2. Create ClusterRole which read permissions on ingress rule and services
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/002_cluster_role.yaml
```

3. Create ClusterRoleBinding between cluster role and service account
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/003_cluster_role_binding.yaml
```

4. Create Secret for ovh api key and kubernetes cluster api
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/004_secret.yaml
```

5. Create Deployments
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/005_deployments.yaml
```


## Built With
* [Kubernetes Python Api](https://pypi.org/project/kubernetes/)
* [OVH Client](https://pypi.org/project/ovh/) - Api to talk with dns in OVH
* [PyTZ](https://pypi.org/project/pytz/)
## Authors
* **[Filippo Ferrazini](https://github.com/Filippo125)** - *Initial work* -
## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
