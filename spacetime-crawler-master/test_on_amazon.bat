ECHO Startup.

set want_to_check=%1

ECHO **** Resetting frontier....
python applications\search\reset_frontier.py -a amazon.ics.uci.edu -p 9100

ECHO **** Done resetting frontier.
ECHO **** Starting to crawl....
python applications\search\crawler.py -a amazon.ics.uci.edu -p 9100
ECHO **** Done crawling.

IF %1=="check" GOTO CHECK

:CHECK
ECHO **** Checking frontier....
python applications\search\check_frontier.py -a amazon.ics.uci.edu -p 9100
ECHO **** Done checking frontier.