# nanoloom: a minimalistic [Loom](https://github.com/socketteer/loom) CLI
import orjson
from nanoloom.shuttle import Shuttle
from nanoloom.tapestry import Tapestry, Node
from nanoloom import utils

from typing import Tuple
import os

def load(filename: str, backend: str) -> Tuple[Tapestry, Shuttle]:
    if not os.path.sep in filename:
        filename = os.path.join('tapestries', filename)
    with open(filename, 'rb') as f:
        data = orjson.loads(f.read())
    tapestry = Tapestry({node['id']: Node(**node) for node in data['tapestry']['nodes']}, data['tapestry']['root'], data['tapestry'].get('metadata', {}))
    if 'name' not in tapestry.metadata:
        tapestry.metadata['name'] = filename.split('.')[0]
    shuttle = Shuttle(tapestry, data['shuttle'], backend)
    return tapestry, shuttle

def save(tapestry: Tapestry, shuttle: Shuttle, filename: str) -> None:
    if not os.path.sep in filename:
        filename = os.path.join('tapestries', filename)
        if not os.path.exists('tapestries'):
            os.mkdir('tapestries')
    with open(filename, 'wb') as f:
        f.write(orjson.dumps({
            'tapestry': {
                'nodes': [node.__dict__ for node in tapestry.nodes.values()],
                'root': tapestry.root,
                'metadata': tapestry.metadata,
            },
            'shuttle': shuttle.node
        }))

if __name__ == '__main__':
    import argparse, dotenv
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description='nanoloom: a minimal Loom CLI')
    parser.add_argument('--version', action='version', version='nanoloom vα.1 (build 20240727.1)')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    parser.add_argument('--backend', '-b', default='openai', help='choose a backend (openai, anthropic, huggingface, pytorch)', type=str, choices=['openai', 'anthropic', 'replicate', 'huggingface', 'pytorch'])
    parser.add_argument('--temperature', '-t', default=0.7, help='temperature for sampling', type=float)
    parser.add_argument('--max_tokens', '-m', default=100, help='max tokens for sampling', type=int)
    parser.add_argument('--model', required=True, help='model for sampling', type=str)
    parser.add_argument('--num_samples', '-n', default=1, help='number of samples to generate', type=int)
    parser.add_argument('--stop', default=None, help='stop sequence for sampling', type=str)
    parser.add_argument('--top_k', default=0, help='top_k for sampling', type=int)
    parser.add_argument('--top_p', default=0.9, help='top_p for sampling', type=float)
    parser.add_argument('--presence_penalty', default=0.0, help='presence penalty for sampling', type=float)
    parser.add_argument('--frequency_penalty', default=0.0, help='frequency penalty for sampling', type=float)
    parser.add_argument('--stream', action='store_true', help='stream output (for supported backends)')
    args = parser.parse_args()
    
    generation_params = {
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'model': args.model,
        'num_samples': args.num_samples,
        'stop': args.stop,
        'top_k': args.top_k,
        'top_p': args.top_p,
        'presence_penalty': args.presence_penalty,
        'frequency_penalty': args.frequency_penalty
    }

    # Clear none values from generation_params
    generation_params = {k: v for k, v in generation_params.items() if v is not None}

    tapestry = None
    shuttle = None

    while True:
        if tapestry is None:
            action = input('> ')
            if action == 'n':
                root_data = input('root data> ')
                root = Node('root', root_data, {}, None, [])
                tapestry = Tapestry({'root': root}, 'root')
                shuttle = Shuttle(tapestry, 'root', args.backend)
            elif action == 'l':
                filename = input('filename> ')
                filename = filename if filename.endswith('.json') else filename + '.json'
                tapestry, shuttle = load(filename, args.backend)
                print(f'loaded from {filename}')
            elif action == 'q':
                break
            elif action == 'h':
                print('n: new tapestry')
                print('l: load tapestry')
                print('q: quit')
            else:
                print('Invalid action')
        else:
            print(shuttle.get_state())
            action = input('> ')
            if action == 'fw':
                shuttle.forward()
            elif action == 'rw':
                shuttle.backward()
            elif action == '>':
                shuttle.right()
            elif action == '<':
                shuttle.left()
            elif action == 'i':
                data = input('data> ')
                shuttle.insert(data)
            elif action == 'e':
                data = utils.rlinput('data> ', shuttle.get_node().data)
                shuttle.edit(data)
            elif action == 'g':
                shuttle.generate(**generation_params)
            elif action == 's':
                if 'name' not in tapestry.metadata:
                    name = input('filename> ')
                    name = name.split('.')[0] if name.endswith('.json') else name
                    tapestry.metadata['name'] = name
                save(tapestry, shuttle, f"{tapestry.metadata['name']}.json")
                print(f'saved to {tapestry.metadata["name"]}.json')
            elif action == 'sas':
                filename = input('filename> ')
                filename = filename if filename.endswith('.json') else filename + '.json'
                tapestry.metadata['name'] = filename.split('.')[0]
                save(tapestry, shuttle, filename)
                print(f'saved to {filename}')
            elif action == 'l':
                filename = input('filename> ')
                filename = filename if filename.endswith('.json') else filename + '.json'
                tapestry, shuttle = load(filename, args.backend)
                print(f'loaded from {filename}')
            elif action == 'q':
                break
            elif action == 'h':
                print('fw: forward')
                print('bw: backward')
                print('> : right')
                print('< : left')
                print('i : insert')
                print('e : edit')
                print('g : generate')
                print('s : save')
                print('l : load')
                print('q : quit')
            else:
                print('Invalid action')