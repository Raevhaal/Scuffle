import requests
from multiprocessing import queues #pyinstaller workaround  https://stackoverflow.com/questions/40768570/importerror-no-module-named-queue-while-running-my-app-freezed-with-cx-freeze
import json

CURRENT_VERSION = '0.1.3'

def check_version(force_print=False):

    new_version_available = False
    if 'dev' in CURRENT_VERSION:
        print("SCUFFLE version check disabled.")
        print("DEVELOPER NOTE: Remember to update VersionChecker.CURRENT_VERSION before publishing a release.")
    else:
        try:
            r = requests.get('https://api.github.com/repos/rougelite/SCUFFLE/releases/latest')

            #https://api.github.com
            #GET /repos/:owner/:repo/releases/latest
            if r.ok:
                repoItem = json.loads(r.text or r.content)
                repoTag = repoItem['tag_name']
                print("")
                if (repoTag != CURRENT_VERSION):
                    print("A new version of SCUFFLE is available.")
                    new_version_available = True
                #if (repoTag != CURRENT_VERSION or force_print):
                    print(repoItem['html_url'])
                    #print("Release Notes:")
                    #print(repoItem['body'])
                    print('')
                else:
                    print("SCUFFLE is up to date.")
            else:
                print("Unable to contact github repo")
        except:
            print("SCUFFLE version check failed (no internet?).")
    print("")
    return new_version_available


if __name__ == '__main__':
    check_version()