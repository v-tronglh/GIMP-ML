virtualenv env
source env/bin/activate
pip install -r requirements.txt
deactivate

chmod +x fcn_resnet101_semseg.py
