import click
from dotenv import load_dotenv
from multi_send_test import multi_send_test

load_dotenv()

@click.command()
@click.option('--prompt',
    prompt='Prompt',
    required=True,
    help='Prompt'
)
def run(
    prompt: str
):
    multi_send_test()
if __name__ == '__main__':
    run()
