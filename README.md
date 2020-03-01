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
kubectl create serviceaccount depdnssa
```
2. Create ClusterRole wich read permissions on ingress rule and services
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/cluster_role.yaml
```
3. Create ClusterRoleBinding between cluster role and service account
```
kubectl apply -f  https://raw.githubusercontent.com/Filippo125/k8s-deploy-external-dns/master/doc/cluster_role_binding.yaml
```

### Coming soon

## Built With
* [Kubernetes Python Api](https://pypi.org/project/kubernetes/)
* [OVH Client](https://pypi.org/project/ovh/) - Api to talk with dns in OVH
* [PyTZ](https://pypi.org/project/pytz/)
## Authors
* **Filippo Ferrazini** - *Initial work* - https://github.com/Filippo12
## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.txt) file for details
