from __future__ import annotations

from collections.abc import Sequence


MODEL_ID = "textplus-bbaw/transnormer-19c-beta-v02"


class Transnormer:
    def __init__(
        self,
        model_id: str = MODEL_ID,
        device: str = "auto",
        batch_size: int = 4,
        num_beams: int = 4,
        show_progress: bool = True,
    ) -> None:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self._torch = torch
        self.device = torch.device(device)
        self.batch_size = batch_size
        self.num_beams = num_beams
        self.show_progress = show_progress
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(self.device)
        self.model.eval()

    def normalize_many(self, texts: Sequence[str]) -> list[str]:
        from tqdm import tqdm

        results: list[str] = []
        with tqdm(
            total=len(texts),
            desc="Normalizing XML",
            unit="segment",
            disable=not self.show_progress,
        ) as progress:
            for start in range(0, len(texts), self.batch_size):
                batch = list(texts[start : start + self.batch_size])
                encoded = self.tokenizer(batch, return_tensors="pt", padding=True)
                input_length = int(encoded.input_ids.shape[1])
                if input_length > 512:
                    raise ValueError(
                        f"A normalization segment has {input_length} byte tokens; "
                        "the model was trained with a maximum of 512."
                    )
                encoded = {name: value.to(self.device) for name, value in encoded.items()}
                with self._torch.inference_mode():
                    outputs = self.model.generate(
                        **encoded,
                        num_beams=self.num_beams,
                        max_new_tokens=512,
                    )
                results.extend(self.tokenizer.batch_decode(outputs, skip_special_tokens=True))
                progress.update(len(batch))
        return results
