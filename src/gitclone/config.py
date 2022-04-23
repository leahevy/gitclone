from yamlable import YamlAble, yaml_info


@yaml_info(yaml_tag_ns="gitclone")
class Config(YamlAble):
    def __init__(self, autofetch={}, other=None, dest="."):
        self.autofetch = autofetch
        self.other = other
