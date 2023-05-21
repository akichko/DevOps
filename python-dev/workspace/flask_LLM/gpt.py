## MIT License
 #
 # Copyright (c) 2023 akichko
 # 
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 # 
 # The above copyright notice and this permission notice shall be included in all
 # copies or substantial portions of the Software.
 # 
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.

from transformers import T5Tokenizer, AutoModelForCausalLM
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from abc import ABCMeta, abstractmethod
from typing import List
import torch
from transformers import Trainer, TrainerCallback


class CustomCallback(TrainerCallback):
    def __init__(self):
        self.step = -1
        self.total_steps = -1
        self.progress_percentage = -1
        
    def on_step_end(self, args, state, control, model=None, **kwargs):
        self.step = state.global_step
        self.total_steps = state.max_steps
        self.progress_percentage = (self.step / self.total_steps) * 100
        #print(f"進捗率: {self.progress_percentage}%")

    
    def on_train_begin(self, args, state, control, model=None, **kwargs):
        self.step = 0
        #print("トレーニングを開始します。")
        return
              
    def on_train_end(self, args, state, control, model=None, **kwargs):
        #print("学習が完了しました")
        return


class Gpt(metaclass=ABCMeta):
    
    # @property
    # @abstractmethod
    # def is_trainable(self):
        # pass
    
    @property
    def train_status(self):
        return self._train_status

    @train_status.setter
    def train_status(self, value):
        self._train_status = value
    
    @abstractmethod
    def generate(self, text, max_length=150, num_return_sequences=1) -> List[str]:
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass


class GptDummy(Gpt):
    
    is_trainable = False
    
    def __init__(self, addtext):
        self.addtext = addtext

    # @property
    # def is_trainable(self):
    #     return False
    
    def generate(self, text, max_length=150, num_return_sequences=1) -> List[str]:
        full_text_array = []
        for i in range(num_return_sequences):
            full_text_array.append(text + self.addtext + '」' + str(i) + 'あいうえお')

        return full_text_array

    def get_status(self) -> str:
        return f'{self.addtext}'
    
class Gpt2(Gpt):
    
    is_trainable = True
    train_status = 0 # 0:未開始,1:学習中,2:学習完了
    
    def __init__(self, path):
        self.path = path
        #self.tokenizer = T5Tokenizer.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(path)
        self.train_status = 0
        self.customCallback = CustomCallback()

    # @property
    # def is_trainable(self):
    #     return True
    
    def generate(self, text, max_length=150, num_return_sequences=1):
        input = self.tokenizer.encode(text, return_tensors="pt", add_special_tokens=False)

        output = self.model.generate(input,
                        min_length=50,
                        max_length=max_length,
                        do_sample=True,
                        top_k=500,
                        top_p=0.95,
                        num_return_sequences=num_return_sequences,
                        pad_token_id=self.tokenizer.pad_token_id,
                        bos_token_id=self.tokenizer.bos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id)

        return self.tokenizer.batch_decode(output, skip_special_tokens=True)
    
    
    def finetune(self, train_data, output_dir, num_train_epochs=3, batch_size=32):
        if self.is_trainable == False:
            return
        
        self.train_status = 1

        from transformers import TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments
        
        train_dataset = TextDataset(
            tokenizer=self.tokenizer,
            file_path=train_data,
            block_size=128)
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False,
        )
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=10_000,
            save_total_limit=1,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
            callbacks=[self.customCallback]  # カスタムコールバッククラスのインスタンスを渡す
        )
        
        trainer.train()
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        self.train_status = 2


    def prompt_tuning(self, prompt, document):
        encoded_prompt = self.tokenizer(prompt, padding=True, truncation=True, return_tensors="pt")
        encoded_doc = self.tokenizer(document, padding=True, truncation=True, return_tensors="pt")
        input_ids = torch.cat((encoded_prompt['input_ids'], encoded_doc['input_ids'][:, 1:]), dim=1)
        attention_mask = torch.cat((encoded_prompt['attention_mask'], encoded_doc['attention_mask'][:, 1:]), dim=1)
        logits = self.model(input_ids=input_ids, attention_mask=attention_mask)[0]
        scores = logits.softmax(dim=1)[:, 1]
        sorted_scores, sorted_indices = scores.sort(descending=True)
        top_index = sorted_indices[0][0].item()
        optimized_prompt = self.tokenizer.decode(input_ids[0][:(top_index+1)])
        return optimized_prompt

    def get_status(self) -> str:
        if self.train_status == 0:
            return f"通常({self.path})"
        elif self.train_status == 1:
            return f"学習中（進捗率: {round(self.customCallback.progress_percentage)}%）"
        elif self.train_status == 2:
            return f"学習完了"
        else:
            return "エラー"
