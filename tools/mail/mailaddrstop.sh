for iPid in `ps aux | grep python |  grep mailaddr.py | awk '{print $2}'`; do kill -9 ${iPid}; done