Student Number: 23079215
Name: linwei zhu


1. Create a Python virtual environment:python -m venv venv

2. Install dependencies:
   pip install -r requirements.txt -i  https://pypi.tuna.tsinghua.edu.cn/simple

3. Modify the database connection:
   Modify the database configuration in the `config.py` file.

4. Create tables:
   $env: app = "app"
   flask db init # Initialize the database, only needs to be executed once
   flask db migrate # Generate migration files
   flask db upgrade # Execute migration files

5. Start the project:
   python app.py runserver

6. Access the project:
   Frontend: 127.0.0.1:5002