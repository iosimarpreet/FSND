sed -i 's/app.run()/manager.run()/g' app.py

python3 app.py db migrate
python3 app.py db upgrade

sed -i 's/manager.run()/app.run()/g' app.py
