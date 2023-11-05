from llama_index.llms import HuggingFaceLLM
import torch


def get_llm():
    return HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=256,
        generate_kwargs={"temperature": 0.25, "do_sample": True, "top_p": 0.5},
        # query_wrapper_prompt=PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>"),
        # tokenizer_name="mistralai/Mistral-7B-v0.1",
        tokenizer_name="stabilityai/stablelm-3b-4e1t",
        # model_name="mistralai/Mistral-7B-v0.1",
        model_name="stabilityai/stablelm-3b-4e1t",
        model_kwargs={"trust_remote_code": True, "torch_dtype": torch.float32, "use_safetensors": True},
        # model_kwargs={"offload_folder": "offload"},
        # device_map="auto",
        device_map="cpu",
        tokenizer_kwargs={"max_length": 4096},
    )
