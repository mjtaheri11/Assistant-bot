from langchain_community.embeddings import HuggingFaceEmbeddings
from config import config

embedding_model = HuggingFaceEmbeddings(
    model_name="/home/user01/.cache/huggingface/hub/models--alefbot--alef-zibert/snapshots/b5a9d43b612b57191bb3a618b51b09b8ecabd927",
    model_kwargs={"device": config["embedding_model"]["device"]}
)
