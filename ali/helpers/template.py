import json

from ruamel.yaml import YAML


class TemplateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Ref):
            return {"Ref": o.reference}
        if isinstance(o, GetAtt):
            return {"Fn::GetAtt": [o.reference, o.attribute]}
        else:
            return json.JSONEncoder.default(self, o)


class Ref:
    yaml_tag = u"!Ref"

    def __init__(self, reference):
        self.reference = reference

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.reference)

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


class GetAtt:
    yaml_tag = u"!GetAtt"

    def __init__(self, att_ref):
        fields = att_ref.split(".")
        if len(fields) != 2:
            raise ValueError(
                '!GetAtt {} does not match "<resource>.<attribute>"'.format(att_ref)
            )
        self.reference = fields[0]
        self.attribute = fields[1]

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            cls.yaml_tag, "{reference}.{attribute}".format(node)
        )

    @classmethod
    def from_yaml(cls, constructor, node):
        return cls(node.value)


yaml = YAML(typ="safe", pure=True)
yaml.register_class(Ref)
yaml.register_class(GetAtt)


def load_template(stream):
    return yaml.load(stream)


def template_to_string(o):
    return json.dumps(o, cls=TemplateEncoder)
