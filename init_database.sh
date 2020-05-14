export FLASK_APP=CUIT_TP &&
flask db init &&
flask db migrate &&
flask db upgrade