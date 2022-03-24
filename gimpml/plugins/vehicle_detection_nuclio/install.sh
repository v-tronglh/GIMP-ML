virtualenv env
source env/bin/activate
pip install -r requirements.txt
deactivate

chmod +x vehicle_detection_nuclio.py
