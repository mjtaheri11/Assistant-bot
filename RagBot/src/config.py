import yaml
import pathlib


CONFIG_ADDR = "{path}/rag-configs.yaml".format(path=pathlib.Path(__file__).parent.resolve())
config = yaml.safe_load(open(CONFIG_ADDR, "r", encoding="utf-8"))
