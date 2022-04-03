"""
this is the driver code that will implement EgyBest, Movie and Series classes
and also call the four function in the INPUTS file to take inputs from the user
"""

from egybest import *
from inputs import *
import sys

available_args = (
    ('-m', '--movie'),
    ('-s', '--series'),
    ('-n', '--name'),
    ('-q', '--quality'),
    ('-se', '--season'),
    ('-l', '--list'),
)


def check_availability(arg):
    pass


def help():
    print('''
    -m, --movie, -s, --series           to specify the type movies/series respectively.
    -n, --name                          to type the name of the movie/series.    
    -q, --quality                       to specify the quality.
    -se, --season                       to specify the season of the series (used only for series with -s specifier).
    -l, --list                          to specify the episodes of the series (used only for series with -s specifier).
                ''')
    sys.exit(0)


def main():

    # '''
    #     movie: -m -n -q
    #     series: -s -n -q --season=#num --list=()
    #         if --list is empty then download all episodes
    # '''
    #
    # args = sys.argv
    #
    # # no args are provided
    # if len(args) == 1:
    #     print('Syntax error!\nNo arguments were provided! See -h, --help for more details.')
    #     sys.exit(0)
    #
    # if len(args) == 2 and args[1] in ('--help', '-h'):
    #     help()
    #
    # else:
    #     if len(args) < 3:
    #         # movie type
    #         if args[1] in ('-m', '--movie'):
    #             print("Movie type args is not complete. See -h, --help for more help.")
    #             sys.exit(0)
    #
    #         if args[1] in ('-s', '--series'):
    #             print("Series type args is not complete. See -h, --help for more help.")
    #             sys.exit(0)
    #
    #         else:
    #             print("Syntax error!\nSee -h, --help for more help.")
    #             sys.exit(0)
    #
    #     if 3 < len(args) < 6:
    #         if args[1] in ('-s', '--series'):
    #             print("Series type args is not complete. See -h, --help for more help.")
    #             sys.exit(0)
    #
    #     if len(args) > 6:
    #         print("args is unknown. See -h, --help for more help.")
    #         sys.exit(0)
    #
    #     if args[1] in ('-m', '--movie'):
    #         if len(args) == 4:
    #             type = 'movie'
    #             for i in args:
    #                 # if i in ('-n', '--name'):
    #                 #     name =
    #                 i = i.split('=')
    #                 if i[0] in ('-n', '--name'):
    #                     name = i[1]
    #                 if i[1] in ('-q', '--quality'):
    #                     quality = i[1]
    #
    #     if args[1] in ('-s', '--series'):
    #         if len(args) == 6:
    #             type = 'series'
    #             for i in args:
    #                 i = i.split('=')
    #                 if i[0] in ('-n', '--name'):
    #                     name = i[1]
    #                 if i[1] in ('-q', '--quality'):
    #                     quality = i[2]
    #                 if i[2] in ('-se', '--season'):
    #                     season = i[3]
    #                 if
    #
    # exit(0)
    getTypeAndName()
    chooseQuality()
    with open('inputs.txt', 'r') as f:
        line = f.readline().strip().split()
        quality = line[-1]
        type = line[-2]
        name = ' '.join(line[:-2]).strip()

    if type == 'movie':  # type is movie
        Movie(name, quality)

    else:  # type series
        getSeason()  # get the desired season
        getEpisodes()  # get the desired episodes
        with open('inputs.txt', 'r') as f:
            f.readline()
            season, *episodes = f.readline().strip().split()
        
        if episodes[0] == 'all':
            pass

        elif episodes[0].endswith(':'):
            pass
        
        else:
            episodes = [int(e) for e in episodes]

        Series(name, quality, season, episodes)


if __name__ == '__main__':
    main()
