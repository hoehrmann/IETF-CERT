import sys
import click
from llama_cpp import Llama, LlamaGrammar, StoppingCriteriaList


@click.command()
@click.option(
    "-m",
    "--model",
    type=click.Path(exists=True),
)
@click.option(
    "-t",
    "--template",
    type=click.File("r"),
)
@click.option(
    "-g",
    "--gbnf",
    type=click.File("r"),
)
@click.option(
    "-d",
    "--draft",
    type=click.File("r"),
)
@click.option("-n", "--n_ctx", default=8192, type=int)
def main(model, template, gbnf, draft, n_ctx):

    grammar = LlamaGrammar.from_string(gbnf.read())
    model = Llama(model_path=model, n_ctx=n_ctx)
    prompt_text = template.read()

    seen_command = False
    seen_junk = False

    def stop(tokens, *args, **kwargs):
        if seen_command and tokens[-1] in [model.token_nl(), model.token_eos()]:
            return True
        if seen_junk:
            return True
        return False

    generated = ""

    for token in model.create_completion(
        prompt_text,
        grammar=grammar,
        stream=True,
        max_tokens=512,
        stopping_criteria=StoppingCriteriaList([stop]),
        
    ):
        text = token["choices"][0]["text"]
        generated += text

        for line in generated.split("\n")[:-1]:
            if line.startswith("Comment: "):
                pass
            elif line.startswith("$ "):
                seen_command = True
            elif line.startswith("Summary "):
                pass
            elif line.startswith("Note to self:"):
                pass
            else:
                seen_junk = True

        print(text, end="")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
