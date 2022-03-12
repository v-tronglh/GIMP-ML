if python --version 2>&1 | grep -q "^Python 2\."; then
    echo "Python 2 found."
    python -m pip install virtualenv
    python -m virtualenv env
elif python2 --version 2>&1 | grep -q "^Python 2\."; then
    echo "Python 2 found."
    python2 -m pip install virtualenv
    python2 -m virtualenv env
else
    echo "Python 2 not found! Please install Python 2 then execute this script again!"
    exit
fi

source env/bin/activate
pip install -r requirements.txt
deactivate

chmod +x ../pl_fcn_resnet101_semseg.py
