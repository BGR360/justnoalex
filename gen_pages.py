#!/usr/bin/env python3

import argparse
import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape


# Thanks @tzot
# https://stackoverflow.com/a/600612
def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def render_template(env, template_name, context, outfile):
    template = env.get_template(template_name)
    rendered = template.render(context)
    outfile.write(rendered)


def gen_pages(input_dir, print_fn):
    config_path = os.path.join(input_dir, 'config.json')
    with open(config_path) as config_file:
        configs = json.load(config_file)

    # Clear out www/.
    www_dir = os.path.join(input_dir, 'www')
    if os.path.exists(www_dir):
        shutil.rmtree(www_dir)

    # If static/ exists, copy that to www/.
    # Otherwise, create empty www/.
    static_dir = os.path.join(input_dir, 'static')
    if os.path.exists(static_dir):
        def copy_fn(src, dst, *args):
            # This is what copytree() calls by default.
            shutil.copy2(src, dst, *args)
            print_fn(f'Copied {src} --> {dst}')
        shutil.copytree(static_dir, www_dir, copy_function=copy_fn)
    else:
        os.mkdir(www_dir)

    # Create Jinja environment
    templates_path = os.path.join(input_dir, 'templates')
    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape()
    )

    # Render templates to www/
    for config in configs:
        # Normalize config
        if 'canonical_path' not in config:
            config['canonical_path'] = config['path']

        # Render template
        template_name = config['template']
        out_path = os.path.join(www_dir, config['path'])
        with open(out_path, 'w') as outfile:
            render_template(env, template_name, config, outfile)
        print_fn(f'Rendered {template_name} --> {out_path}')


def main():
    parser = argparse.ArgumentParser(description='Generate site HTML')
    parser.add_argument(
        'input',
        help='Path to directory containing config.json and templates/ directory',
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Don\'t be verbose.',
    )
    args = parser.parse_args()
    if args.quiet:
        print_fn = lambda _: None
    else:
        print_fn = print
    gen_pages(args.input, print_fn)


if __name__ == '__main__':
    main()
