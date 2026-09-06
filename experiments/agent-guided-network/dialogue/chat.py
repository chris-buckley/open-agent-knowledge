"""Use a standalone research model through direct Python or the lowered OAK program."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime import Program, Session


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Export directory containing model.json and program.json.')
    parser.add_argument('--engine', choices=('python', 'oak'), default='oak')
    parser.add_argument('--demo', type=Path, help='JSON with a users array; prints actual replies and exits.')
    args = parser.parse_args()
    filename = 'model.json' if args.engine == 'python' else 'program.json'
    record = json.loads((args.directory / filename).read_text())
    constructor = Session if args.engine == 'python' else Program
    session = constructor(record)

    def answer(text: str) -> str:
        if isinstance(session, Session):
            return session.answer(text)
        return session.run('interface.chat', {'TEXTS': [text]})['REPLIES'][0]

    if args.demo:
        for user in json.loads(args.demo.read_text())['users']:
            print('You:', user)
            print('Model:', answer(user))
        return
    print('Research only: four objects and four rooms; often wrong, especially when information is missing.')
    print('Commands: /reset, /save, /load, /quit. State is saved to dialogue-state.json in the export directory.')
    while True:
        try:
            text = input('You: ')
        except EOFError:
            break
        try:
            if text == '/quit':
                break
            if text == '/reset':
                session = constructor(record)
            elif text == '/save':
                (args.directory / 'dialogue-state.json').write_text(json.dumps(session.snapshot()))
            elif text == '/load':
                session.restore(json.loads((args.directory / 'dialogue-state.json').read_text()))
            else:
                print('Model:', answer(text))
        except (ValueError, OSError) as error:
            print('Input/state error:', error)


if __name__ == '__main__':
    main()
