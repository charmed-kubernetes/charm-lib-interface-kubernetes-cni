import hashlib
import os


class KubernetesCniProvides:
    """Implements the Provides side of the kubernetes-cni interface."""

    def __init__(self, charm, endpoint, default_cni):
        self.charm = charm
        self.endpoint = endpoint
        self.default_cni = default_cni

    @property
    def cidr(self):
        relation = self.default_relation
        if not relation:
            return None
        for unit in relation.units:
            cidr = relation.data[unit].get("cidr")
            if cidr:
                return cidr

    @property
    def cni_conf_file(self):
        relation = self.default_relation
        if not relation:
            return None
        for unit in relation.units:
            cni_conf_file = relation.data[unit].get("cni-conf-file")
            if cni_conf_file:
                return cni_conf_file

    @property
    def default_relation(self):
        if self.default_cni:
            relations = [
                relation
                for relation in self.relations
                if relation.app.name == self.default_cni
            ]
        else:
            relations = sorted(self.relations, key=lambda relation: relation.app.name)
        return relations[0] if relations else None

    @property
    def relations(self):
        return self.charm.model.relations[self.endpoint]

    def set_image_registry(self, registry):
        for relation in self.relations:
            relation.data[self.unit]["image-registry"] = registry

    def set_service_cidr(self, service_cidr):
        for relation in self.relations:
            relation.data[self.unit]["service-cidr"] = service_cidr

    def set_kubeconfig_hash_from_file(self, path):
        kubeconfig_hash = hash_file(path)
        for relation in self.relations:
            relation.data[self.unit]["kubeconfig-hash"] = kubeconfig_hash

    @property
    def unit(self):
        return self.charm.unit


def hash_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        contents = f.read()
    m = hashlib.sha256()
    m.update(contents)
    return m.hexdigest()
