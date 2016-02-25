export PYTHONPATH=$PYTHONPATH:~/Eclipse/src
rm ~/Eclipse/src/cerebral/dog1/listener-eclipse ~/Eclipse/src/cerebral/dog1/worker1.pid ~/Eclipse/src/cerebral/manager.pid
cd ~/Eclipse/src/cerebral/dog1
date -s "24 FEB 2016"
python3 main.py