import argparse
from painter import Corner, LogoPainter
import os


def path(s):
    if os.path.exists(s):
        return s
    else:
        raise argparse.ArgumentTypeError('Entered path does NOT exist!')


if __name__ == '__main__':
    cliparser = argparse.ArgumentParser()
    cliparser.add_argument('-l', '--logo', type=path, help='Path to logo image', required=True)
    cliparser.add_argument('-t', '--target', type=path, help='Path to target image or directory', required=True)
    cliparser.add_argument('-s', '--save_to', default='result', help='Path to result directory')
    cliparser.add_argument('--rewrite', action='store_true', help='Check this to add logo to source images')
    cliparser.add_argument('--logo-resize-rate', type=float, default=0.2, help='Logo min dimension / Img min dimension')
    cliparser.add_argument('--margin-rate', type=float, default=0.01, help='Margin size / Img min dimension')
    cliparser.add_argument('--min-logo-min-dim', type=int, default=300,
                           help='px, minimum size of logo min dimension')
    cliparser.add_argument('-c', '--corner', choices=['TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_LEFT', 'BOTTOM_RIGHT'],
                           default='BOTTOM_RIGHT', help='Choose an image corner where to place your logo')

    args = cliparser.parse_args()
    if not args.rewrite:
        save_to_path = args.save_to
    else:
        if os.path.isfile(args.target):
            save_to_path = os.path.dirname(args.target)
        else:
            save_to_path = args.target

    LogoPainter(args.logo, args.target, save_to_path=save_to_path, logo_resize_rate=args.logo_resize_rate,
                margin_rate=args.margin_rate, corner=Corner.__dict__[args.corner],
                min_logo_min_dim=args.min_logo_min_dim).process_all()
