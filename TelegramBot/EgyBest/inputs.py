from colors import Colors
import sys


def getTypeAndName():
    #  get a movie | series
    try:
        type = input(f'* Enter what you desired (movie/m) | (series/s): ').strip().lower()
        if type in ('quit', 'q'):
            sys.exit(0)

        while True:
            if type not in ('movie', 'm', 'series', 's', 'quit', 'q'):
                type = input(f'{Colors.WARNING}    *** Please Enter on of these (move/m | series/s) ***{Colors.ENDC}\n'
                            '* Enter what you desired (movie/m) | (series/s): ').strip().lower()
            
            else:
                break
            
            # terminate
            if type in ('quit', 'q'):
                sys.exit(0)
            

        name, season = '', ''
        if type in ('series', 's'):
            name = input(f'    * Enter your series name: ').strip().lower()
            type = 'series'

        elif type in ('movie', 'm'):
            name = input(f'    * Enter your movie name: ').strip().lower()
            type = 'movie'

        # write to the file
        with open('inputs.txt', 'w') as f:
            f.write(f'{name} {type} ')

        return name, type
    
    except KeyboardInterrupt as e:
        print()
        sys.exit(0)


def chooseQuality():
    try:
        quality = int(input(f'       * Choose quality (1080 | 720 | 480 | 360 | 240): '))
        while True:
            if quality not in (1080, 720, 480, 360, 240):
                quality = int(input(
                    f'{Colors.WARNING}       * Choose quality (1080 | 720 | 480 | 360 | 240): {Colors.ENDC}'))
            else:
                break

        with open('inputs.txt', 'a') as f:
            f.write(f'{quality}\n')
    
    except KeyboardInterrupt as e:
        print()
        sys.exit(0)


# get season of the series
def getSeason() -> int:
    try:
        season = input(f'       * Enter the season: ').strip()
        # validate that the season is a number
        while not season.isnumeric():
            season = input(f'{Colors.WARNING}    *** Season must be a number!{Colors.ENDC}\n'
                        '       * Enter the season: ').strip()
        season = int(season)
        with open('inputs.txt', 'a') as f:
            f.write(f'{season} ')

        return season
    
    except KeyboardInterrupt as e:
        print()
        sys.exit(0)


# get the episodes
def getEpisodes():
    try:
        i = 1
        ep = input(
            f'          * Enter an episode number ("all" to choose all, "#number:" to choose all episodes from #number)\n             {i} # ').strip().lower()
        episodes = []

        while ep not in ('quit', 'q'):
            # if the input was 'all' then break it
            if ep == 'all':
                episodes = 'all'
                break

            if ep.endswith(':'):
                episodes = ep
                break
            
            # it's not a number
            while not ep.isnumeric():

                ep = input(f'{Colors.WARNING}             *** Episode isn\'t a number or "all" ***{Colors.ENDC}\n'
                           f'          * Enter the episode (type "all" to choose them all, "#number:" to choose all episodes from #number)\n             {i} # ').strip().lower()
                
                # terminate
                if ep in ('all', 'quit', 'q') or ep.endswith(':'):
                    break

            # if the input was 'all' then break it
            if ep == 'all':
                episodes = 'all'
                break
                
            if ep.endswith(':'):
                episodes = ep
                break

            # terminate
            if ep in ('quit', 'q'):
                break

            # get a number of episode
            episodes.append(int(ep))

            i += 1
            ep = input(f'             {i} # ').strip().lower()

        if isinstance(episodes, list):
            episodes.sort()
            with open('inputs.txt', 'a') as f:
                for e in episodes:
                    f.write(f'{e} ')
                f.write('\n')

        else:
            with open('inputs.txt', 'a') as f:
                f.write(f'{episodes}')

        return episodes

    except KeyboardInterrupt as e:
        print()
        sys.exit(0)
