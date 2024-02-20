from models.opt import OPTAPForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

if __name__ == '__main__':
    o_model_path = 'facebook/opt-1.3b'
    q_model_path = 'cache/models/opt-1.3b.pt'
    supported_bits = [3, 4]

    tokenizer = AutoTokenizer.from_pretrained(o_model_path)
    config = AutoConfig.from_pretrained(o_model_path, trust_remote_code=True)
    # model = AutoModelForCausalLM.from_pretrained(o_model_path)
    model = OPTAPForCausalLM.from_quantized(q_model_path, o_model_path, config.max_position_embeddings, supported_bits=supported_bits)
    # TODO : Why the model is already in GPU?
    model = model.eval().cuda()

    input_context = "I'm cat person, "
    input_ids = tokenizer.encode(input_context, return_tensors="pt")
    output = model.generate(input_ids.cuda(), max_length=256)
    output_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(output_text)