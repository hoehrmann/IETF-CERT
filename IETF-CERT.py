import collections
import re
import sys
import click
from llama_cpp import Llama, LlamaGrammar, StoppingCriteriaList
import rich
from itertools import accumulate
import copy

def read_draft(draft: click.File):
    pages = draft.read().rstrip("\r\n\t\f ").split("\f")

    def quote(page):
        quoted = "\n".join(["> " + line for line in page.split("\n")])
        quoted = quoted.rstrip(">\r\n\t\f ")
        quoted += (
            "\n\n"
            + "<!-- End of page. Start with your expert review summary! "
            + "Then proceed as instructed earlier! There are more pages you must read "
            + "and review. Use the command `$ page N` to proceed to "
            + "the next page. -->\n"
        )
        return quoted

    return [[{"type": "draft", "text": quote(page)}] for page in pages]


# def takewhile_it_fits(iterator, weight_func, capacity):
#     weight = 0
#     for elem in iterator:
#         weight += weight_func(elem)
#         if weight > capacity:
#             return
#         yield elem


def count_tokens(model, message):
    total = 0
    for part in message:
        tokens = model.tokenize(part["content"].encode("utf-8"))
        # FIXME: No good way to compute this plus the size added
        # by chat template stuff
        total += len(tokens) + 10
    return total


def to_message(page):
    return [
        {
            "type": p["type"],
            "role": "user" if p["type"] == "draft" else "assistant",
            "content": p["text"],
        }
        for p in page
    ]


def to_full(message):
    return [p for p in message]


def to_medium(message):
    for m in message:
        if m["type"] == 'draft':
            c = copy.deepcopy(m)
            c["content"] = "> [...]\n\n"
            yield c
        else:
            yield m

def to_minimal(message):
    for m in message:
        if m["type"] == 'draft':
            c = copy.deepcopy(m)
            c["content"] = "> [...]\n\n"
            yield c
        if m["type"] == "comment":
            pass
        else:
            yield m

def flatten(xss):
    return [x for xs in xss for x in xs]


def prompt_pages(pages, model, total):
    remainder = total

    i = iter(reversed(list([to_message(p) for p in pages])))

    # TODO(bh): write this differently

    try:

        # Allocate 50% of available space to full details (everything included)
        current_total = 0
        while True:
            message = to_full(next(i))
            size = count_tokens(model, message)
            if (current_total + size) > (remainder / 2):
                break
            yield message
            current_total += size

        remainder -= current_total

        # Allocate 50% of the remainder to medium details (original text excluded)
        current_total = 0
        while True:
            message = to_medium(next(i))
            size = count_tokens(model, message)
            if (current_total + size) > (remainder / 2):
                break
            yield message
            current_total += size

        remainder -= current_total

        # Allocate the remainder to minimal details (original text and comments excluded)
        while remainder > 0:
            message = to_minimal(next(i))
            size = count_tokens(model, message)
            if size > remainder:
                break
            yield message
            remainder -= size
    except StopIteration:
        pass


def prepare_prompt(base_prompt, pages, model, n_ctx):
    n_ctx -= count_tokens(model, [{"content": base_prompt}])
    return [{"role": "system", "content": base_prompt}] + flatten(
        reversed(list(prompt_pages(pages, model, n_ctx)))
    )


def format_messages(messages):
    # TODO(bh): groupby role to avoid repeated headers. Might also make sense
    # to actually group them coming out of the model, repeated assistant
    # tokens might affect performance.
    result = ""
    for message in messages:
        if "role" in message:
            result += message["role"].upper() + ":\n"
        if "content" in message:
            result += message["content"] + "\n"

    return result


def complete_page(model: Llama, grammar, messages):
    generated = ""

    print(format_messages(messages))

    for token in model.create_chat_completion(
        messages,
        grammar=grammar,
        stream=True,
        max_tokens=256,
    ):

        # rich.print(token)
        if "content" not in token["choices"][0]["delta"]:
            rich.print(token)
            continue

        text = token["choices"][0]["delta"]["content"]
        generated += text

        # FIXME: Should expect a newline
        if re.search(r"\$ page \d+\D", generated):
            rich.print("Found page command", token)
            break

        if len(generated) > 1000:
            break

        print(text, end="")
        sys.stdout.flush()

    page = []

    for line in generated.split("\n"):
        if line.startswith("Comment: "):
            page.append({"type": "comment", "text": line})
        elif line.startswith("$ "):
            # page.append({"type": "cmd", "text": line})
            # TODO: add result of command
            # For now let's just impute a command
            pass
        elif line.startswith("Summary of page "):
            page.append({"type": "summary", "text": line})
        elif line.startswith("Note to self:"):
            page.append({"type": "note", "text": line})
        else:
            pass

    return page


@click.command()
@click.option(
    "-m",
    "--model",
    "model_path",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "-t",
    "--template",
    type=click.File("r"),
    required=True,
)
@click.option(
    "-g",
    "--gbnf",
    type=click.File("r"),
    required=True,
)
@click.option(
    "-d",
    "--draft",
    type=click.File("r"),
    required=True,
)
@click.option("-n", "--n_ctx", default=8192, type=int)
def main(model_path, template, gbnf, draft, n_ctx):

    draft_pages = read_draft(draft)

    template_vars = collections.defaultdict(dict)
    template_vars["ietfcert.pagecount"] = str(len(draft_pages))

    base_prompt = template.read()

    def subst(m: re.Match):
        return template_vars.get(m.group(1), None) or "null"

    base_prompt = re.sub(r"\{\{(ietfcert\.\w+)\}\}", subst, base_prompt)

    print(base_prompt)

    grammar = LlamaGrammar.from_string(gbnf.read())
    model = Llama(model_path=model_path, n_ctx=n_ctx)

    for nth in range(len(draft_pages)):
        sliced = draft_pages[: nth + 1]

        # Right now we ignore commands and just pretend the next page is requested.
        sliced[-1].insert(0, {"type": "cmd", "text": f"$ page {nth+1}\n"})
        prompt = prepare_prompt(base_prompt, sliced, model, n_ctx)

        processed = complete_page(model, grammar, prompt)
        sliced[-1].extend(processed)


if __name__ == "__main__":
    main()
